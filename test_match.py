script_map = {
    "TOP_COVER":    "mesh_top_cover_complete.py",
    "OUTER_RACE":   "mesh_races.py",
    "MID_RACE":     "mesh_races.py",
    "INNER_RACE":   "mesh_races.py",
    "BEARING_TOP":  "mesh_races.py",
    "BEARING_BOTTOM":"mesh_races.py",
    "SHAFT":        "mesh_shaft.py",
    "STATOR":       "mesh_stator.py",
    "ROTOR_RING":   "mesh_rotor_ring.py",
    "PCB_BRACKET":  "mesh_pcb_bracket.py",
    "DISPLAY_PCB":  "mesh_display_pcb.py",
    "PCB":          "mesh_display_pcb.py",
    "BOTTOM_COVER": "mesh_bottom_cover.py",
    "EPS_PACKAGING":"mesh_EPS.py",
    "BODY":         "mesh_body.py",
}

def test_match(comp_name):
    base_name = comp_name
    check_name = comp_name.replace(" ", "_").upper()
    for standard in script_map:
        if check_name == standard or check_name.startswith(standard + "_"):
            base_name = standard
            break
    print(f"'{comp_name}' -> '{base_name}' -> {script_map.get(base_name, 'mesh_body.py')}")

test_match("EPS_PACKAGING_1")
test_match("EPS_PACKAGING_2")
