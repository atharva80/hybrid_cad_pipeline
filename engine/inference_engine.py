#!/usr/bin/env python3
"""
inference_engine.py
===================
Decoupled inference backend for the Hybrid CAD Parsing Pipeline.
Import and call `infer_cad(step_path)` from any entrypoint (CLI, GUI, etc.)
Returns a structured dictionary of classified components and their records.
"""

import os
import sys
import numpy as np
import pandas as pd
import xgboost as xgb
import pyvista as pv

# ── Ensure the package root is on the path when run standalone ─────────────
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.step_loader import load_step_xcaf, extract_solids, _read_name
from core.feature_extractor import extract_all
from heuristics.phase1_anchors import identify_anchors
from heuristics.phase2_housing import identify_housing
from heuristics.phase3_bearings import identify_bearings
from heuristics.phase4_pcb import identify_pcb

from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.BRep import BRep_Tool
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location

# ── Paths ──────────────────────────────────────────────────────────────────
_MODELS_DIR = os.path.join(_ROOT, "models")


def _solid_to_pyvista(shape):
    BRepMesh_IncrementalMesh(shape, 0.5)
    vertices, faces_pv, vertex_offset = [], [], 0
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face(exp.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is not None:
            for i in range(1, tri.NbNodes() + 1):
                p = tri.Node(i)
                if not loc.IsIdentity():
                    p.Transform(loc.Transformation())
                vertices.append([p.X(), p.Y(), p.Z()])
            for i in range(1, tri.NbTriangles() + 1):
                t = tri.Triangle(i)
                faces_pv.extend([3, t.Value(1) - 1 + vertex_offset,
                                     t.Value(2) - 1 + vertex_offset,
                                     t.Value(3) - 1 + vertex_offset])
            vertex_offset += tri.NbNodes()
        exp.Next()
    if not vertices:
        return None
    return pv.PolyData(np.array(vertices, dtype=np.float32),
                       np.array(faces_pv, dtype=np.int32))


def infer_cad(step_file_path: str) -> dict:
    """
    Run the full hybrid heuristic + ML inference pipeline on a STEP file.

    Returns
    -------
    dict with keys:
        records   : list of solid records (geometry + features)
        results   : list of (label, [node_indices], confidence)
        doc       : OpenCASCADE document (for STEP export)
    """
    print(f"\n=============================================")
    print(f"🚀 HYBRID INFERENCING: {os.path.basename(step_file_path)}")
    print(f"=============================================")

    # ── Phase 1: Heuristic Anchor Detection ────────────────────────────────
    print("\n[Phase 1] Running Topological Heuristic Filters...")
    p1 = identify_anchors(step_file_path)
    records = p1["RECORDS"]
    stator_cands = p1["STATOR_CANDIDATES"]
    shaft_cands  = p1["SHAFT_CANDIDATES"]
    print(f"  -> {len(stator_cands)} STATOR candidates, {len(shaft_cands)} SHAFT candidates found.")

    # ── Stage 1 ML: Anchor Resolution ──────────────────────────────────────
    xgb_anchors = xgb.XGBClassifier()
    xgb_anchors.load_model(os.path.join(_MODELS_DIR, "xgb_anchors.json"))

    def _resolve_anchor(candidates, class_idx, name):
        if len(candidates) == 1:
            print(f"  ✔️  {name} locked by Heuristics: Solid #{candidates[0]}")
            return candidates[0], 1.0
        print(f"  ⚠️  Multiple/Zero {name}s. Triggering Stage 1 ML Fallback...")
        eval_nodes = candidates if candidates else list(range(len(records)))
        rows = []
        for i in eval_nodes:
            f  = records[i].features
            bb = f.get("_bbox", [0]*6)
            dx, dy, dz = bb[3]-bb[0], bb[4]-bb[1], bb[5]-bb[2]
            extents = [dx, dy, dz]
            if min(extents) == 0:
                ar = 0
            else:
                ax = extents.index(min(extents))
                rad = [a for a in range(3) if a != ax]
                dia   = max(bb[a+3]-bb[a] for a in rad)
                thick = extents[ax]
                ar = thick / dia if dia > 0 else 0
            rows.append({"face_count": f.get("face_count", 0), "aspect_ratio": ar})
        df   = pd.DataFrame(rows)
        probs = xgb_anchors.predict_proba(df)[:, class_idx]
        best = int(np.argmax(probs))
        node = eval_nodes[best]
        conf = float(probs[best])
        print(f"  🤖 ML Resolved {name}: Solid #{node} (Conf: {conf*100:.1f}%)")
        return node, conf

    stator_node, st_conf = _resolve_anchor(stator_cands, 1, "STATOR")
    p1["STATOR_CANDIDATES"] = [stator_node]
    p1["STATOR"]            = stator_node

    st_bb   = records[stator_node].features.get("_bbox")
    dx, dy, dz = st_bb[3]-st_bb[0], st_bb[4]-st_bb[1], st_bb[5]-st_bb[2]
    extents   = [dx, dy, dz]
    motor_axis = extents.index(min(extents))
    rad_axes   = [a for a in range(3) if a != motor_axis]
    st_cen     = [(st_bb[a+3]+st_bb[a])/2 for a in range(3)]
    st_dia     = max(st_bb[a+3]-st_bb[a] for a in rad_axes)
    st_vol     = records[stator_node].features.get("volume_mm3", 1.0)
    st_thick   = st_bb[motor_axis+3] - st_bb[motor_axis]
    up_vector  = p1.get("UP_VECTOR", 1)

    # ── Stage 2 ML: Component Resolver ─────────────────────────────────────
    xgb_comp = xgb.XGBClassifier()
    xgb_comp.load_model(os.path.join(_MODELS_DIR, "xgboost_model.json"))

    def _resolve_component(cands, target_class_idx, name_str):
        if len(cands) == 1:
            return cands[0], 1.0
        eval_nodes = cands if len(cands) > 0 else [
            i for i, r in enumerate(records) if r.features.get("volume_mm3", 0) > 50
        ]
        rows = []
        for i in eval_nodes:
            f  = records[i].features
            bb = f.get("_bbox")
            if not bb:
                continue
            cen   = [(bb[a]+bb[a+3])/2 for a in range(3)]
            thick = bb[motor_axis+3] - bb[motor_axis]
            dia   = max(bb[a+3]-bb[a] for a in rad_axes)
            rows.append((i, {
                "face_count":        f.get("face_count", 0),
                "aspect_ratio":      f.get("aspect_min_max", 0),
                "vol_ratio":         f.get("volume_mm3", 0) / st_vol if st_vol > 0 else 0,
                "dia_ratio":         dia / st_dia if st_dia > 0 else 0,
                "thick_ratio":       thick / st_thick if st_thick > 0 else 0,
                "radial_dist":       np.sqrt(sum((cen[a]-st_cen[a])**2 for a in rad_axes)),
                "z_dist_to_stator":  (cen[motor_axis] - st_cen[motor_axis]) * up_vector,
                "touches_top_bearing": 0,
                "touches_bot_bearing": 0,
                "is_wider_than_stator": 1 if dia > st_dia else 0,
            }))
        if not rows:
            return None, 0.0
        df_eval  = pd.DataFrame([r[1] for r in rows])
        features = ["face_count","aspect_ratio","vol_ratio","dia_ratio",
                    "thick_ratio","radial_dist","z_dist_to_stator",
                    "touches_top_bearing","touches_bot_bearing","is_wider_than_stator"]
        probs    = xgb_comp.predict_proba(df_eval[features])[:, target_class_idx]
        best     = int(np.argmax(probs))
        node     = rows[best][0]
        conf     = float(probs[best])
        print(f"  🤖 ML Resolved {name_str}: Solid #{node} (Conf: {conf*100:.1f}%)")
        return node, conf

    # Resolve shaft first (bearings and PCB depend on it)
    shaft_eval         = shaft_cands if shaft_cands else list(range(len(records)))
    shaft_node, sh_conf = _resolve_component(shaft_eval, 2, "SHAFT")
    p1["SHAFT"] = shaft_node

    # ── Phase 2-4: Heuristic Filters ───────────────────────────────────────
    print("\n[Phase 2-4] Running Housing, Bearing, PCB Heuristics...")
    p2 = identify_housing(step_file_path, p1)
    p3 = identify_bearings(step_file_path, p1)
    p4 = identify_pcb(step_file_path, p1)

    tc_node,    tc_conf    = _resolve_component(p2["TOP_COVER_CANDIDATES"],    6, "TOP_COVER")
    bc_node,    bc_conf    = _resolve_component(p2["BOTTOM_COVER_CANDIDATES"], 7, "BOTTOM_COVER")
    ti_node,    ti_conf    = _resolve_component(p1.get("INSULATOR_CANDIDATES", []), 3, "TOP_INSULATOR")
    bi_node,    bi_conf    = _resolve_component(p1.get("INSULATOR_CANDIDATES", []), 4, "BOTTOM_INSULATOR")
    rotor_node, rotor_conf = _resolve_component(p1.get("ROTOR_CANDIDATES", []), 5, "ROTOR_RING")

    pcb_nodes  = p4.get("PCB_PLATES", [])
    if len(pcb_nodes) > 1:
        # Pick only the largest plate by radial diameter
        pcb_nodes = [max(pcb_nodes, key=lambda n: max(records[n].features.get("_bbox", [0]*6)[a+3]-records[n].features.get("_bbox", [0]*6)[a] for a in rad_axes))]
    brg_a_nodes = p3.get("BEARING_A", {}).get("CLUSTER_NODES", [])
    brg_b_nodes = p3.get("BEARING_B", {}).get("CLUSTER_NODES", [])

    # ── Final Results ───────────────────────────────────────────────────────
    results = [
        ("STATOR",           [stator_node],                       st_conf),
        ("SHAFT",            [shaft_node]  if shaft_node  else [], sh_conf),
        ("ROTOR_RING",       [rotor_node]  if rotor_node  else [], rotor_conf),
        ("TOP_COVER",        [tc_node]     if tc_node     else [], tc_conf),
        ("BOTTOM_COVER",     [bc_node]     if bc_node     else [], bc_conf),
        ("TOP_INSULATOR",    [ti_node]     if ti_node     else [], ti_conf),
        ("BOTTOM_INSULATOR", [bi_node]     if bi_node     else [], bi_conf),
        ("PCB",              pcb_nodes,                            1.0),
        ("BEARING_TOP",      brg_a_nodes,                          1.0),
        ("BEARING_BOTTOM",   brg_b_nodes,                          1.0),
    ]

    print("\n=============================================")
    print("🏆 INFERENCE RESULTS")
    print("=============================================")
    for comp, nodes, conf in results:
        for node in nodes:
            if node is None:
                continue
            name = _read_name(records[node].label)
            print(f"  {comp.ljust(16)} : Solid #{str(node).ljust(3)} | "
                  f"Conf: {conf*100:5.1f}% | Name: {name}")

    return {
        "records": records,
        "results": results,
        "doc":     p1["DOC"],
    }


def render_results(inference_output: dict, out_dir: str, cad_basename: str):
    """
    Save a PNG render of each classified component into out_dir.
    """
    os.makedirs(out_dir, exist_ok=True)
    records = inference_output["records"]
    results = inference_output["results"]

    print(f"\n📸 Rendering identified parts to: {out_dir}")
    for comp, nodes, _ in results:
        if not nodes:
            continue
        try:
            plotter    = pv.Plotter(off_screen=True)
            added_mesh = False
            for node in nodes:
                if node is None:
                    continue
                mesh = _solid_to_pyvista(records[node].shape)
                if mesh:
                    plotter.add_mesh(mesh, color="lightblue", show_edges=False,
                                     smooth_shading=True, specular=0.5)
                    added_mesh = True
            if added_mesh:
                plotter.view_isometric()
                img_path = os.path.join(out_dir, f"{cad_basename}_{comp}.png")
                plotter.screenshot(img_path)
                plotter.close()
                print(f"  Saved {comp} → {img_path}")
        except Exception as e:
            print(f"  ❌ Failed to render {comp}: {e}")
