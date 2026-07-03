#!/usr/bin/env python3
"""
phase2_housing.py
=================
Identifies the TOP_COVER housing relative to the Phase 1 anchors.
"""

import numpy as np
from core.config import load_heuristics_config

def identify_housing(input_path: str, phase1_results: dict):
    cfg = load_heuristics_config()["phase2_housing"]
    records = phase1_results['RECORDS']
    # Removed old single node lookups since Phase 1 now returns lists
    motor_axis = phase1_results['MOTOR_AXIS']
    
    top_cover_cands = []
    bottom_cover_cands = []
    
    # Since Phase 1 now returns STATOR_CANDIDATES, we use the first one temporarily
    stator_cands = phase1_results.get('STATOR_CANDIDATES', [])
    stator_node = stator_cands[0] if stator_cands else None
    
    if stator_node is not None:
        st_bb = records[stator_node].features.get('_bbox')
        rad_axes = [a for a in range(3) if a != motor_axis]
        st_center = [(st_bb[a+3]+st_bb[a])/2 for a in range(3)]
        st_dia = max(st_bb[a+3]-st_bb[a] for a in rad_axes)
        
        above_cands = []
        below_cands = []
        for i, r in enumerate(records):
            # We must make sure not to include ANY of the phase 1 candidates
            skip_nodes = set(
                phase1_results.get('STATOR_CANDIDATES', []) +
                phase1_results.get('SHAFT_CANDIDATES', []) +
                phase1_results.get('ROTOR_CANDIDATES', []) +
                phase1_results.get('INSULATOR_CANDIDATES', [])
            )
            if i in skip_nodes:
                continue
                
            f = r.features
            bb = f.get('_bbox')
            if not bb: continue
            
            rad_dist = np.sqrt(sum(( ((bb[a+3]+bb[a])/2) - st_center[a] )**2 for a in rad_axes))
            dia = max(bb[a+3]-bb[a] for a in rad_axes)
            
            # Must be roughly coaxial and wider than the stator
            if rad_dist < cfg["rad_dist_max"] and st_dia + cfg["dia_min_offset"] < dia < st_dia + cfg["dia_max_offset"]:
                # Must have complex geometry (rejects simple dummy boxes and flat brackets)
                if f.get('face_count', 0) > cfg["face_count_min"]:
                    min_z, max_z = bb[motor_axis], bb[motor_axis+3]
                    z_cen = (min_z + max_z) / 2
                    s_min, s_max = st_bb[motor_axis], st_bb[motor_axis+3]
                    stator_center_z = (s_min + s_max) / 2
                    
                    up_vector = phase1_results.get('UP_VECTOR', 1)
                    if (z_cen * up_vector) > (stator_center_z * up_vector):
                        above_cands.append(i)
                    else:
                        below_cands.append(i)
                            
        if above_cands:
            top_cover_cands = above_cands
        if below_cands:
            bottom_cover_cands = below_cands
            
    return {
        "TOP_COVER_CANDIDATES": top_cover_cands,
        "BOTTOM_COVER_CANDIDATES": bottom_cover_cands
    }

if __name__ == "__main__":
    from phase1_anchors import identify_anchors
    
    fpath = '/media/atharva/WD Gen3 SSD/Atomberg/CAD/prime.STEP'
    print(f"Running Phase 1 on {fpath}...")
    p1 = identify_anchors(fpath)
    
    print("Running Phase 2...")
    p2 = identify_housing(fpath, p1)
    
    tc_cands = p2['TOP_COVER_CANDIDATES']
    print(f"TOP_COVER_CANDIDATES: {len(tc_cands)} found. ({tc_cands})")
