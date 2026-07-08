import os, glob, re

template_dir = "/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates"
files = glob.glob(os.path.join(template_dir, "mesh_*.py"))

for fpath in files:
    with open(fpath, "r") as f:
        content = f.read()

    safeguard_regex = r"    # -- ROBUST BODY CHECK --\n    _mdl = \"\$Geometry\" if \"MODEL\" not in locals\(\) else MODEL\n    _check_bods = simlab.getBodiesWithSubString\(_mdl, \[BODY_NAME\]\)\n    if not _check_bods:\n        print\(f\"WARNING: Body '\{BODY_NAME\}' does NOT exist in model '\{_mdl\}'!\"\)\n        print\(f\"Skipping \{BODY_NAME\} gracefully to prevent UI freeze.\"\)\n        return\n"
    
    robust_safeguard = """    # -- ROBUST BODY CHECK --
    _all_mdls = simlab.getAllRootModelNames("all")
    _actual_cad = "$Geometry"
    if _all_mdls:
        for m in _all_mdls:
            if not m.endswith(".gda") and "_SM" not in m:
                _actual_cad = m
                break
    _mdl = _actual_cad if "MODEL" not in locals() else MODEL
    if _mdl == "$Geometry" and _actual_cad != "$Geometry":
        _mdl = _actual_cad
        
    _check_bods = simlab.getBodiesWithSubString(_mdl, [BODY_NAME])
    if not _check_bods:
        print(f"WARNING: Body '{BODY_NAME}' does NOT exist in model '{_mdl}'!")
        print(f"Skipping {BODY_NAME} gracefully to prevent UI freeze.")
        return
"""
    
    new_content = re.sub(safeguard_regex, robust_safeguard, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(fpath, "w") as f:
            f.write(new_content)
        print(f"Fixed safeguard model resolution in {os.path.basename(fpath)}")
    else:
        # Check if they already have the fixed one
        if "_actual_cad" not in content:
            print(f"Could not find regex in {os.path.basename(fpath)}")

