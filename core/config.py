import os
import yaml

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_CONFIG_PATH = os.path.join(_ROOT, "config", "heuristics_config.yaml")

_DEFAULT_CONFIG = {
    "phase1_anchors": {
        "global_min_vol": 50,
        "stator_min_vol": 3000,
        "stator_dia_min": 80.0,
        "stator_dia_max": 120.0,
        "stator_thick_min": 8.0,
        "stator_thick_max": 35.0,
        "stator_aspect_max": 0.35,
        "stator_complex_faces": 100,
        "shaft_len_min": 40.0,
        "shaft_len_max": 180.0,
        "shaft_dia_max": 30.0,
        "shaft_rad_dist_max": 5.0,
        "rotor_inner_len_min": 30.0,
        "rotor_inner_dia_max": 60.0,
        "rotor_inner_rad_dist_max": 5.0,
        "rotor_outer_dia_tolerance": 15.0,
        "rotor_outer_face_min": 400,
        "rotor_outer_vol_max": 15000.0,
        "rotor_alt_rad_dist_max": 5.0,
        "rotor_alt_dia_min_offset": 1.0,
        "rotor_alt_dia_max_offset": 30.0,
        "rotor_alt_aspect_max: 0.6": 0.6,
        "rotor_alt_thick_tolerance": 10.0,
        "rotor_alt_vol_min": 5000.0
    },
    "phase2_housing": {
        "rad_dist_max": 20.0,
        "dia_min_offset": -5.0,
        "dia_max_offset": 120.0,
        "face_count_min": 150
    },
    "phase3_bearings": {
        "rad_dist_max": 2.0,
        "dia_max_mult": 3.0,
        "faces_max": 50,
        "height_min": 1.5,
        "z_center_tolerance": 6.0,
        "cluster_min_nodes": 2
    },
    "phase4_pcb": {
        "height_min": 1.4,
        "height_max": 2.0,
        "dia_min": 40.0,
        "rad_dist_max": 10.0,
        "faces_min": 30
    },
    "phase5_eps": {
        "vol_mult_min": 1.5,
        "dia_mult_min": 1.5,
        "fill_ratio_min": 0.25
    },
    "phase6_canopies": {
        "fill_ratio_min": 0.15,
        "aspect_ratio_max": 0.30,
        "dia_min": 40.0
    }
}

def load_heuristics_config():
    if not os.path.exists(_CONFIG_PATH):
        print(f"Warning: {_CONFIG_PATH} not found. Falling back to defaults.")
        return _DEFAULT_CONFIG
    try:
        with open(_CONFIG_PATH, "r") as f:
            user_cfg = yaml.safe_load(f) or {}
            
        # Deep merge with defaults to ensure all keys exist even if user deletes them
        merged = {}
        for phase, default_dict in _DEFAULT_CONFIG.items():
            merged[phase] = default_dict.copy()
            if phase in user_cfg and isinstance(user_cfg[phase], dict):
                merged[phase].update(user_cfg[phase])
        return merged
    except Exception as e:
        print(f"Error loading yaml config: {e}. Falling back to defaults.")
        return _DEFAULT_CONFIG
