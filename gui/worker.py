"""
worker.py — Background inference thread for the Hybrid CAD Pipeline GUI.
Runs infer_cad() + render_results() off the main thread and emits signals
for phase transitions, console output, and final results.
"""

import os
import sys
import glob
import traceback
from io import StringIO

from PySide6.QtCore import QThread, Signal, QObject


# ── stdout redirector ─────────────────────────────────────────────────────
class _StreamBridge(QObject):
    """Captures print() calls and forwards them as Qt signals."""
    text_written = Signal(str)

    def write(self, text: str):
        if text:
            self.text_written.emit(text)

    def flush(self):
        pass


# ── Phase token patterns ──────────────────────────────────────────────────
_PHASE_TOKENS = {
    "[Phase 1]":                 ("phase1",  1),   # (key, step_index)
    "Stage 1 ML Fallback":       ("ml1",     2),
    "":                         ("ml1",     2),
    "[Phase 5]":                 ("phase5",  3),
    "ML Resolved SHAFT":         ("ml2a",    4),
    "[Phase 2-4]":               ("phase24", 5),
    "ML Resolved TOP_COVER":     ("ml2b",    6),
    "ML Resolved BOTTOM_COVER":  ("ml2b",    6),
    "ML Resolved ROTOR":         ("ml2b",    6),
    "Phase 6":                   ("phase6",  7),
    " INFERENCE RESULTS":       ("done",    8),
}


class InferenceWorker(QThread):
    """
    Runs the full 6-phase pipeline in a background thread.

    Signals
    -------
    console_line   : str          — new line of text to display
    phase_changed  : str          — phase key (see _PHASE_TOKENS)
    file_started   : str          — path of the STEP file being processed
    file_done      : tuple        — (step_path, inference_result_dict, out_dir)
    batch_progress : tuple        — (current_index, total)
    finished_all   : None         — emitted when every file is processed
    error_occurred : str          — human-readable error message
    """
    console_line   = Signal(str)
    phase_changed  = Signal(str)
    file_started   = Signal(str)
    file_done      = Signal(object, object, str)  # (path, result, out_dir)
    batch_progress = Signal(int, int)
    finished_all   = Signal()
    error_occurred = Signal(str)

    def __init__(self, step_paths: list, render_dir: str = None, export_dir: str = None,
                 expected_components: list = None,
                 do_render: bool = True, do_export: bool = False):
        super().__init__()
        self.step_paths  = step_paths if isinstance(step_paths, list) else [step_paths]
        self.render_dir  = render_dir
        self.export_dir  = export_dir
        self.expected_components = expected_components if expected_components is not None else []
        self.do_render   = do_render
        self.do_export   = do_export
        self._abort      = False

        # Lazy import so the worker only loads heavy libs when run
        self._engine     = None
        self._exporter   = None

    def abort(self):
        self._abort = True

    def _load_engine(self):
        """Import heavy pipeline modules (deferred to worker thread)."""
        _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if _ROOT not in sys.path:
            sys.path.insert(0, _ROOT)
        from engine.inference_engine import infer_cad
        self._infer_cad = infer_cad
        
        if self.do_render:
            from engine.inference_engine import render_results
            self._render_results = render_results
        
        if self.do_export:
            from engine.step_exporter import export_named_step
            self._export_named_step = export_named_step
        else:
            self._export_named_step = None

    def _collect_steps(self):
        files = []
        for p in self.step_paths:
            if os.path.isdir(p):
                exts = ("*.step", "*.STEP", "*.stp", "*.STP")
                for ext in exts:
                    files.extend(glob.glob(os.path.join(p, ext)))
            elif os.path.isfile(p):
                files.append(p)
        return sorted(list(set(files)))

    def run(self):
        # Redirect stdout so pipeline prints go to the console widget
        bridge = _StreamBridge()
        bridge.text_written.connect(self._on_text)
        _old_stdout = sys.stdout
        sys.stdout  = bridge

        try:
            self._load_engine()
            files = self._collect_steps()
            total = len(files)
            self.console_line.emit(f"  Found {total} STEP file(s)\n\n")

            for idx, step_file in enumerate(files):
                if self._abort:
                    self.console_line.emit("\n  Run aborted by user.\n")
                    break

                self.batch_progress.emit(idx + 1, total)
                self.file_started.emit(step_file)

                cad_name = os.path.splitext(os.path.basename(step_file))[0]
                model_render_out = None

                try:
                    result = self._infer_cad(step_file, expected_components=self.expected_components)
                    import time; time.sleep(0.05)  # Yield GIL before heavy rendering

                    if self.do_render and self.render_dir:
                        model_render_out = os.path.join(self.render_dir, cad_name)
                        os.makedirs(model_render_out, exist_ok=True)
                        self._render_results(result, model_render_out, cad_name)

                    if self.do_export and self.export_dir and self._export_named_step:
                        os.makedirs(self.export_dir, exist_ok=True)
                        step_out = os.path.join(self.export_dir, f"{cad_name}_NAMED.step")
                        self._export_named_step(result, step_out)

                    self.file_done.emit(step_file, result, model_render_out)

                except Exception as e:
                    msg = f"  Error on {cad_name}:\n{traceback.format_exc()}\n"
                    self.console_line.emit(msg)
                    self.error_occurred.emit(str(e))

            self.finished_all.emit()

        except Exception as e:
            self.error_occurred.emit(traceback.format_exc())
        finally:
            sys.stdout = _old_stdout

    def _on_text(self, text: str):
        self.console_line.emit(text)
        # Detect phase transitions
        for token, (key, _) in _PHASE_TOKENS.items():
            if token in text:
                self.phase_changed.emit(key)
                break
