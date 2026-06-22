#!/usr/bin/env python3
"""
phase5_EPS_motorbox.py
======================
Identifies the EPS packaging blocks (motor box / master carton inserts) by leveraging
extreme volumetric scaling and fill-ratio mathematics.
"""

def identify_eps(records, stator_node, motor_axis):
    """
    Identifies EPS Packaging blocks based on relative volume and bounding box fill ratio.
    """
    if stator_node is None:
        return []

    rad_axes = [a for a in range(3) if a != motor_axis]
    st_bb = records[stator_node].features.get("_bbox", [0]*6)
    st_vol = records[stator_node].features.get("volume_mm3", 0)
    st_dia = max(st_bb[a+3] - st_bb[a] for a in rad_axes)

    eps_nodes = []
    
    for i, r in enumerate(records):
        if i == stator_node:
            continue
            
        vol = r.features.get("volume_mm3", 0)
        bb = r.features.get("_bbox", [0]*6)
        dia = max(bb[a+3] - bb[a] for a in rad_axes)
        
        dim_x = bb[3] - bb[0]
        dim_y = bb[4] - bb[1]
        dim_z = bb[5] - bb[2]
        
        bb_vol = max(1, dim_x * dim_y * dim_z)
        fill_ratio = vol / bb_vol
        
        # Core Heuristic: Massive relative volume, wide diameter, dense solid ratio (>25%)
        if vol > st_vol * 1.5 and dia > st_dia * 1.5 and fill_ratio > 0.25:
            eps_nodes.append(i)
            
    return eps_nodes
