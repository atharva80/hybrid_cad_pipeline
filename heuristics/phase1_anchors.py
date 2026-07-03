#!/usr/bin/env python3
"""
phase1_anchors.py
=================
Identifies the 3 global anchors (SHAFT, STATOR, ROTOR_RING) from a ceiling fan motor assembly
using top-down topological heuristics.
"""

import sys
import numpy as np
from pathlib import Path

# Use the local core modules (step_loader and feature_extractor)
from core.step_loader import load_step_xcaf, extract_solids
from core.feature_extractor import extract_all
from core.config import load_heuristics_config

def identify_anchors(input_path: str):
    doc, st = load_step_xcaf(input_path)
    records = extract_solids(st)
    extract_all(records)
    cfg = load_heuristics_config()["phase1_anchors"]
    
    # 1. Volume filter
    valid_nodes = [i for i, r in enumerate(records) if r.features.get('volume_mm3', 0) > cfg["global_min_vol"]]
    
    # 2. Identify STATOR (Anchor)
    stator_candidates = []
    for i in valid_nodes:
        f = records[i].features
        vol = f.get('volume_mm3', 0)
        if vol < cfg["stator_min_vol"]: continue
        
        bb = f.get('_bbox', [0,0,0,0,0,0])
        dx, dy, dz = bb[3]-bb[0], bb[4]-bb[1], bb[5]-bb[2]
        extents = sorted([dx, dy, dz])
        thickness, diameter = extents[0], extents[2]
        
        if diameter > 0:
            aspect = thickness / diameter
            if cfg["stator_dia_min"] < diameter < cfg["stator_dia_max"] and cfg["stator_thick_min"] < thickness < cfg["stator_thick_max"] and aspect < cfg["stator_aspect_max"]:
                stator_candidates.append(i)
                
    # We don't pick a hard stator node here. We return the candidates for the ML model to decide.
    # However, we must intelligently guess the temporary stator node to extract the global motor axis and bounds for the rest of the heuristics.
    temp_stator_node = None
    if stator_candidates:
        complex_cands = [i for i in stator_candidates if records[i].features.get('face_count', 0) > cfg["stator_complex_faces"]]
        if complex_cands:
            temp_stator_node = max(complex_cands, key=lambda i: records[i].features.get('volume_mm3', 0))
        else:
            temp_stator_node = max(stator_candidates, key=lambda i: records[i].features.get('volume_mm3', 0))
    print(f"DEBUG: temp_stator_node resolved to Solid #{temp_stator_node}")

    motor_axis = 2 # default Z
    
    if temp_stator_node is not None:
        st_bb = records[temp_stator_node].features.get('_bbox')
        motor_axis = np.argmin([st_bb[3]-st_bb[0], st_bb[4]-st_bb[1], st_bb[5]-st_bb[2]])
        rad_axes = [a for a in range(3) if a != motor_axis]
        st_center = [(st_bb[a+3]+st_bb[a])/2 for a in range(3)]
        s_min, s_max = st_bb[motor_axis], st_bb[motor_axis+3]
        
        # 3. Identify SHAFT (Relative to Stator)
        shaft_cands = []
        for i in valid_nodes:
            if i == temp_stator_node: continue
            f = records[i].features
            bb = f.get('_bbox')
            if not bb: continue
            
            # Distance from Stator center in radial plane
            rad_dist = np.sqrt(sum(( ((bb[a+3]+bb[a])/2) - st_center[a] )**2 for a in rad_axes))
            length = bb[motor_axis+3] - bb[motor_axis]
            dia = max(bb[a+3]-bb[a] for a in rad_axes)
            min_z, max_z = bb[motor_axis], bb[motor_axis+3]
            length = bb[motor_axis+3] - bb[motor_axis]
            dia = max(bb[a+3]-bb[a] for a in rad_axes)
            if length > cfg["rotor_inner_len_min"] and dia < cfg["rotor_inner_dia_max"]:
                print(f"DEBUG_DUMP #{i}: length={length:.2f}, dia={dia:.2f}, rad_dist={rad_dist:.2f}")
                
            if rad_dist < cfg["shaft_rad_dist_max"]:
                dia = max(bb[a+3]-bb[a] for a in rad_axes)
                min_z, max_z = bb[motor_axis], bb[motor_axis+3]
                
                if cfg["shaft_len_min"] < length < cfg["shaft_len_max"] and dia < cfg["shaft_dia_max"]:
                    # Must physically pass through stator bounds
                    if min_z <= s_max and max_z >= s_min:
                        shaft_cands.append(i)
        
        # We no longer pick the shaft candidate with the highest volume here.

    # 4. Identify TOP and BOTTOM INSULATORS
    insulator_cands = []
    
    if temp_stator_node is not None:
        st_dia = max(st_bb[a+3]-st_bb[a] for a in rad_axes)
        
        insulators = []
        for i in valid_nodes:
            if i == temp_stator_node: continue
            f = records[i].features
            bb = f.get('_bbox')
            if not bb: continue
            
            dia = max(bb[a+3]-bb[a] for a in rad_axes)
            min_z, max_z = bb[motor_axis], bb[motor_axis+3]
            
            # Must share the same diameter profile
            if abs(dia - st_dia) < cfg["rotor_outer_dia_tolerance"]:
                # Must be stacked against the stator core
                if min_z <= s_max + 10 and max_z >= s_min - 10:
                    if f.get('face_count', 0) > cfg["rotor_outer_face_min"] and f.get('volume_mm3', 0) < cfg["rotor_outer_vol_max"]:
                        insulators.append((i, (min_z + max_z)/2))
                        
        up_vector = 1
        if temp_stator_node is not None and shaft_cands:
            st_bb = records[temp_stator_node].features.get('_bbox')
            st_cen = (st_bb[motor_axis] + st_bb[motor_axis+3]) / 2
            sh_bb = records[shaft_cands[0]].features.get('_bbox')
            ext_pos = sh_bb[motor_axis+3] - st_cen
            ext_neg = st_cen - sh_bb[motor_axis]
            up_vector = 1 if ext_pos > ext_neg else -1
            
        if insulators:
            # Sort by Z center scaled by the physical UP direction
            insulators.sort(key=lambda x: x[1] * up_vector)
            insulator_cands = [x[0] for x in insulators]

    # 5. Identify ROTOR RING
    rotor_cands = []
    if temp_stator_node is not None:
        for i in valid_nodes:
            if i == temp_stator_node: continue
            f = records[i].features
            bb = f.get('_bbox')
            if not bb: continue
            
            rad_dist = np.sqrt(sum(( ((bb[a+3]+bb[a])/2) - st_center[a] )**2 for a in rad_axes))
            dia = max(bb[a+3]-bb[a] for a in rad_axes)
            thickness = bb[motor_axis+3] - bb[motor_axis]
            min_z, max_z = bb[motor_axis], bb[motor_axis+3]
            
            # Coaxial and wraps the stator (outer diameter slightly larger)
            if rad_dist < cfg["rotor_alt_rad_dist_max"] and st_dia + cfg["rotor_alt_dia_min_offset"] < dia < st_dia + cfg["rotor_alt_dia_max_offset"]:
                # Z-overlap with stator
                if min_z <= s_max and max_z >= s_min:
                    st_thick = s_max - s_min
                    if dia > 0 and (thickness / dia) < cfg.get("rotor_alt_aspect_max", 0.6) and abs(thickness - st_thick) < cfg["rotor_alt_thick_tolerance"]:
                        if f.get('volume_mm3', 0) > cfg["rotor_alt_vol_min"]:
                            rotor_cands.append(i)
                            
        # We no longer pick a single Rotor Ring node here.
    
    return {
        "SHAFT_CANDIDATES": shaft_cands if 'shaft_cands' in locals() else [],
        "STATOR_CANDIDATES": stator_candidates,
        "INSULATOR_CANDIDATES": insulator_cands,
        "ROTOR_CANDIDATES": rotor_cands if 'rotor_cands' in locals() else [],
        "MOTOR_AXIS": motor_axis,
        "UP_VECTOR": up_vector if 'up_vector' in locals() else 1,
        "RECORDS": records,
        "DOC": doc
    }

if __name__ == "__main__":
    import sys
    fpath = sys.argv[1] if len(sys.argv) > 1 else '/media/atharva/WD Gen3 SSD/Atomberg/CAD/prime.STEP'
    res = identify_anchors(fpath)
    print("--- Phase 1 Candidates Identified ---")
    print(f"Motor Axis: {'XYZ'[res['MOTOR_AXIS']]}")
    for name in ["SHAFT_CANDIDATES", "STATOR_CANDIDATES", "INSULATOR_CANDIDATES", "ROTOR_CANDIDATES"]:
        cands = res[name]
        print(f"{name}: {len(cands)} candidates found. ({cands})")
