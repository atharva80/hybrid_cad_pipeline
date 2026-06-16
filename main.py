#!/usr/bin/env python3
"""
main.py — Hybrid CAD Parsing Pipeline
======================================
Master CLI entrypoint. All flags are documented below.

Usage Examples
--------------
Single file, both renders and named STEP export:
    python main.py --in "path/to/file.step" --imgs ./renders --out ./exports

Single file, renders only (no STEP export):
    python main.py --in "path/to/file.step" --imgs ./renders

Single file, STEP export only (no renders):
    python main.py --in "path/to/file.step" --out ./exports

Batch mode (all STEP files in a folder), both renders and export:
    python main.py --batch "path/to/cad_folder/" --imgs ./renders --out ./exports

Batch mode renders only:
    python main.py --batch "path/to/cad_folder/" --imgs ./renders

Generate SHAP explainability plots for the trained models:
    python main.py --explain
"""

import argparse
import glob
import os
import sys
import time


# ── Path setup so engine can be found ─────────────────────────────────────
_ROOT = os.path.abspath(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


# ── Lazy imports (heavy deps only loaded when actually needed) ─────────────
def _get_engine():
    from engine.inference_engine import infer_cad, render_results
    return infer_cad, render_results


def _get_exporter():
    from engine.step_exporter import export_named_step
    return export_named_step


# ── Helpers ────────────────────────────────────────────────────────────────
def _find_step_files(directory: str) -> list[str]:
    patterns = ["**/*.STEP", "**/*.step"]
    files = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(directory, p), recursive=True))
    return sorted(set(files))


def _process_single(step_path: str, imgs_dir: str | None, out_dir: str | None, expect_pcb_box: bool = False):
    """
    Run the full pipeline on one STEP file.

    - imgs_dir : if set, save PNG renders here (batch: subfolder per assembly)
    - out_dir  : if set, export {name}_NAMED.step here
    - expect_pcb_box: if set, force heuristic extraction of the PCB Box
    """
    infer_cad, render_results = _get_engine()

    t0     = time.time()
    result = infer_cad(step_path, expect_pcb_box)
    elapsed = time.time() - t0
    print(f"\n⏱️  Inference completed in {elapsed:.2f}s")

    basename = os.path.splitext(os.path.basename(step_path))[0]

    if imgs_dir is not None:
        render_results(result, imgs_dir, basename)

    if out_dir is not None:
        export_named_step = _get_exporter()
        export_named_step(result, out_dir, step_path)

    return elapsed


def _batch_mode(batch_dir: str, imgs_root: str | None, out_dir: str | None, expect_pcb_box: bool = False):
    """
    Find all STEP files under batch_dir and process each one.
    If imgs_root is given, each assembly gets its own subfolder:
        imgs_root/{assembly_name}/
    """
    step_files = _find_step_files(batch_dir)
    if not step_files:
        print(f"❌  No STEP files found under: {batch_dir}")
        sys.exit(1)

    print(f"📂  Found {len(step_files)} STEP file(s) in {batch_dir}\n")
    timing = {}

    for idx, fpath in enumerate(step_files, 1):
        basename = os.path.splitext(os.path.basename(fpath))[0]
        print(f"\n{'='*50}")
        print(f"[{idx}/{len(step_files)}]  {basename}")
        print(f"{'='*50}")

        # In batch mode each assembly gets its own render subfolder
        asm_imgs_dir = os.path.join(imgs_root, basename) if imgs_root else None

        try:
            elapsed = _process_single(fpath, asm_imgs_dir, out_dir, expect_pcb_box)
            timing[basename] = elapsed
        except Exception as e:
            print(f"❌  FAILED — {basename}: {e}")
            timing[basename] = -1

    # ── Timing summary ─────────────────────────────────────────────────────
    print(f"\n{'='*50}")
    print("🕒  BATCH TIMING REPORT")
    print(f"{'='*50}")
    total = 0
    for name, t in timing.items():
        status = f"{t:6.2f} sec" if t >= 0 else "  FAILED"
        print(f"  {name.ljust(40)} : {status}")
        total += max(t, 0)
    n_ok = len([t for t in timing.values() if t >= 0])
    print(f"  {'─'*48}")
    print(f"  Total : {total:.2f} sec  |  Avg : {total/n_ok:.2f} sec  |  {n_ok}/{len(step_files)} succeeded")


# ── CLI Definition ──────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description=(
            "Hybrid CAD Parsing Pipeline\n"
            "─────────────────────────────────────────────────────────────────\n"
            "Identifies motor assembly components (Stator, Shaft, Bearings,\n"
            "Covers, Insulators, PCB, Rotor) from unseen CAD STEP files using\n"
            "a hybrid Heuristic + XGBoost ML approach.\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  # Single file — renders + named STEP\n"
            '  python main.py --in Motor.STEP --imgs ./renders --out ./exports\n\n'
            "  # Single file — renders only\n"
            '  python main.py --in Motor.STEP --imgs ./renders\n\n'
            "  # Batch — renders only (each asm gets its own subfolder)\n"
            '  python main.py --batch ./CAD_folder/ --imgs ./renders\n\n'
            "  # Batch — STEP export only\n"
            '  python main.py --batch ./CAD_folder/ --out ./exports\n\n'
            "  # Generate SHAP explainability plots\n"
            '  python main.py --explain\n'
        ),
    )

    # ── Input (mutually exclusive — must pick one) ──────────────────────────
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--in",
        dest="input_file",
        metavar="FILE.step",
        help="Run pipeline on a single STEP file.",
    )
    input_group.add_argument(
        "--batch",
        dest="batch_dir",
        metavar="DIR",
        help="Run pipeline on ALL STEP files found recursively inside DIR.",
    )
    input_group.add_argument(
        "--explain",
        action="store_true",
        default=False,
        help="Generate SHAP feature-importance plots for the trained ML models.",
    )

    # ── Modifiers ──────────────────────────────────────────────────────────
    parser.add_argument(
        "--box",
        action="store_true",
        default=False,
        help="Set this flag if the CAD assembly contains a PCB Box/Enclosure to trigger explicit heuristic searching.",
    )

    # ── Output (at least one required when using --in / --batch) ───────────
    output_group = parser.add_argument_group("output options")
    output_group.add_argument(
        "--imgs",
        dest="imgs_dir",
        metavar="DIR",
        default=None,
        help=(
            "Save PNG renders of each identified component to DIR. "
            "In batch mode, a subfolder per assembly is created automatically."
        ),
    )
    output_group.add_argument(
        "--out",
        dest="out_dir",
        metavar="DIR",
        default=None,
        help=(
            "Export a fully labelled '{name}_NAMED.step' file to DIR. "
            "Internal solid names are replaced with their component class names."
        ),
    )

    return parser


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    parser = build_parser()
    args   = parser.parse_args()

    # ── --explain mode ──────────────────────────────────────────────────────
    if args.explain:
        from engine.explainability import run_shap_explanation
        run_shap_explanation()
        sys.exit(0)

    # ── Validate output flags ───────────────────────────────────────────────
    if args.imgs_dir is None and args.out_dir is None:
        parser.error("At least one output flag is required: --imgs DIR  and/or  --out DIR")

    # ── Single file mode ────────────────────────────────────────────────────
    if args.input_file:
        if not os.path.isfile(args.input_file):
            parser.error(f"File not found: {args.input_file}")
        _process_single(args.input_file, args.imgs_dir, args.out_dir, args.box)

    # ── Batch mode ──────────────────────────────────────────────────────────
    elif args.batch_dir:
        if not os.path.isdir(args.batch_dir):
            parser.error(f"Directory not found: {args.batch_dir}")
        _batch_mode(args.batch_dir, args.imgs_dir, args.out_dir, args.box)


if __name__ == "__main__":
    main()
