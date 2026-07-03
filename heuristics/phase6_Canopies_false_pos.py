import numpy as np
from core.config import load_heuristics_config

def identify_canopies(records, anchors, identified_nodes_set):
    """
    Phase 6: Canopy Extraction (V2 Logic - Permissive, includes false positives)
    Identifies Motor Canopies using the "Process of Elimination" trap.
    """
    cfg = load_heuristics_config()["phase6_canopies"]
    canopy_nodes = []
    
    stator_node = anchors.get("STATOR_NODE")
    shaft_node = anchors.get("SHAFT_NODE")
    motor_axis = anchors.get("MOTOR_AXIS", 2)
    
    rad_axes = [a for a in range(3) if a != motor_axis]
    
    for i, r in enumerate(records):
        if i in identified_nodes_set:
            continue
            
        if stator_node is not None and i == stator_node:
            continue
            
        if shaft_node is not None and i == shaft_node:
            continue
            
        vol = r.features.get("volume_mm3", 0)
        bb = r.features.get("_bbox", [0]*6)
        
        dim_x = max(0.1, bb[3] - bb[0])
        dim_y = max(0.1, bb[4] - bb[1])
        dim_z = max(0.1, bb[5] - bb[2])
        
        bb_vol = dim_x * dim_y * dim_z
        fill_ratio = vol / bb_vol
        
        exts = sorted([dim_x, dim_y, dim_z])
        aspect_ratio_3d = exts[0] / exts[2]
        
        dia = max(bb[a+3] - bb[a] for a in rad_axes)
        
        # --- V2 CANOPY TRAP (Permissive - includes false positives) ---

        # Filter 1: Must be hollow (removes solid brackets, rotors)
        if fill_ratio > cfg["fill_ratio_min"]:
            continue

        # Filter 2: Must not be completely flat (removes washers, thin aesthetic plates)
        if aspect_ratio_3d < cfg["aspect_ratio_max"]:
            continue

        # Filter 3: Basic diameter sanity check (kill tiny screws/collars)
        if dia < cfg["dia_min"]:
            continue

        canopy_nodes.append(i)

    return canopy_nodes
