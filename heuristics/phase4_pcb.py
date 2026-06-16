#!/usr/bin/env python3
"""
phase4_pcb.py
=================
Identifies the PCBA plate(s) from the assembly using standard FR4 thickness heuristics.
"""

import numpy as np

def identify_pcb(input_path: str, phase1_results: dict):
    records = phase1_results['RECORDS']
    motor_axis = phase1_results['MOTOR_AXIS']
    rad_axes = [a for a in range(3) if a != motor_axis]

    shaft_node = phase1_results['SHAFT']
    stator_node = phase1_results['STATOR']
    
    if shaft_node is None or stator_node is None:
        return {"PCB_PLATES": []}

    sh_bb = records[shaft_node].features.get('_bbox')
    sh_center = [(sh_bb[a+3]+sh_bb[a])/2 for a in range(3)]
    
    pcb_nodes = []
    for i, r in enumerate(records):
        if i in [shaft_node, stator_node]: continue
        bb = r.features.get('_bbox')
        if not bb: continue
        
        rad_dist = np.sqrt(sum(( ((bb[a+3]+bb[a])/2) - sh_center[a] )**2 for a in rad_axes))
        dia = max(bb[a+3]-bb[a] for a in rad_axes)
        height = bb[motor_axis+3] - bb[motor_axis]
        faces = r.features.get('face_count', 0)
        
        # Valid PCB plate candidates
        # Standard FR4 thickness is 1.6mm. Bounds 1.4 to 2.0 allow CAD tolerances.
        if 1.4 <= height <= 2.0 and dia > 40.0 and rad_dist < 10.0 and faces > 30:
            pcb_nodes.append(i)
            
    return {"PCB_PLATES": pcb_nodes}

if __name__ == "__main__":
    from phase1_anchors import identify_anchors
    
    fpath = '/media/atharva/WD Gen3 SSD/Atomberg/CAD/prime.STEP'
    print(f"Running Phase 1 on {fpath}...")
    p1 = identify_anchors(fpath)
    
    print("Running Phase 4...")
    p4 = identify_pcb(fpath, p1)
    print("PCB_PLATES:", p4["PCB_PLATES"])
