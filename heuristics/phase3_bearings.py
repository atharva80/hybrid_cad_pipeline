#!/usr/bin/env python3
"""
phase3_bearings.py
=================
Identifies the TOP and BOTTOM bearings (including individual Inner, Outer, and Mid races)
relative to the Phase 1 anchors.
"""

import numpy as np

def identify_bearings(input_path: str, phase1_results: dict):
    records = phase1_results['RECORDS']
    motor_axis = phase1_results['MOTOR_AXIS']
    rad_axes = [a for a in range(3) if a != motor_axis]

    shaft_node = phase1_results['SHAFT']
    stator_node = phase1_results['STATOR']
    
    if shaft_node is None or stator_node is None:
        return {"BEARING_A": {}, "BEARING_B": {}}

    sh_bb = records[shaft_node].features.get('_bbox')
    sh_center = [(sh_bb[a+3]+sh_bb[a])/2 for a in range(3)]
    sh_dia = max(sh_bb[a+3]-sh_bb[a] for a in rad_axes)
    
    st_bb = records[stator_node].features.get('_bbox')
    st_center_z = (st_bb[motor_axis] + st_bb[motor_axis+3]) / 2

    cands = []
    for i, r in enumerate(records):
        if i in [shaft_node, stator_node]: continue
        bb = r.features.get('_bbox')
        if not bb: continue
        
        rad_dist = np.sqrt(sum(( ((bb[a+3]+bb[a])/2) - sh_center[a] )**2 for a in rad_axes))
        dia = max(bb[a+3]-bb[a] for a in rad_axes)
        height = bb[motor_axis+3] - bb[motor_axis]
        faces = r.features.get('face_count', 0)
        
        # Valid bearing race candidates (Scale Invariant)
        if rad_dist < 2.0 and dia < sh_dia * 3.0 and faces < 50 and height > 1.5:
            z = (bb[motor_axis] + bb[motor_axis+3]) / 2
            cands.append({'node': i, 'z': z})
            
    # Cluster by Z-center (allow 6mm tolerance from the initial seed)
    clusters = []
    for c in cands:
        added = False
        for cl in clusters:
            if abs(cl['z_center'] - c['z']) < 6.0:
                cl['nodes'].append(c['node'])
                # Do NOT dynamically update z_center, to prevent cluster drifting
                added = True
                break
        if not added:
            clusters.append({'z_center': c['z'], 'nodes': [c['node']]})
            
    # Valid clusters must have at least 2 components (Inner + Outer race)
    bearing_clusters = [cl for cl in clusters if len(cl['nodes']) >= 2]
    
    # Sort by distance to the stator center to pick the motor bearings (avoids shackle bearings)
    bearing_clusters.sort(key=lambda cl: abs(cl['z_center'] - st_center_z))
    
    def _format_bearing(cl_nodes):
        if not cl_nodes: return {}
        node_dims = []
        for n in cl_nodes:
            bb = records[n].features.get('_bbox')
            dia = max(bb[a+3]-bb[a] for a in rad_axes)
            node_dims.append({'node': n, 'dia': dia})
        
        outer = max(node_dims, key=lambda x: x['dia'])['node']
        inner = min(node_dims, key=lambda x: x['dia'])['node']
        mids = [x['node'] for x in node_dims if x['node'] != outer and x['node'] != inner]
        
        return {
            "CLUSTER_NODES": cl_nodes,
            "OUTER_RACE": outer,
            "INNER_RACE": inner,
            "MID_RACES": mids,
            "Z_CENTER": sum(records[n].features.get('_bbox')[motor_axis] + records[n].features.get('_bbox')[motor_axis+3] for n in cl_nodes) / (2 * len(cl_nodes))
        }
    
    res = {"BEARING_A": {}, "BEARING_B": {}}
    if len(bearing_clusters) > 0:
        res["BEARING_A"] = _format_bearing(bearing_clusters[0]['nodes'])
    if len(bearing_clusters) > 1:
        res["BEARING_B"] = _format_bearing(bearing_clusters[1]['nodes'])
        
    return res

if __name__ == "__main__":
    from phase1_anchors import identify_anchors
    
    fpath = '/media/atharva/WD Gen3 SSD/Atomberg/CAD/prime.STEP'
    print(f"Running Phase 1 on {fpath}...")
    p1 = identify_anchors(fpath)
    
    print("Running Phase 3...")
    p3 = identify_bearings(fpath, p1)
    
    print("BEARING_A:", p3["BEARING_A"])
    print("BEARING_B:", p3["BEARING_B"])
