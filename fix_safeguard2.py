import os, glob, re

template_dir = "/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates"
files = glob.glob(os.path.join(template_dir, "mesh_*.py"))

for fpath in files:
    with open(fpath, "r") as f:
        content = f.read()

    # Find the old robust safeguard block that raises RuntimeError
    safeguard_regex = r"    # -- ROBUST BODY CHECK --.*?prevent freeze\.\"\)\n"
    
    # Replace with graceful exit
    graceful_safeguard = """    # -- ROBUST BODY CHECK --
    _mdl = "$Geometry" if "MODEL" not in locals() else MODEL
    _check_bods = simlab.getBodiesWithSubString(_mdl, [BODY_NAME])
    if not _check_bods:
        print(f"WARNING: Body '{BODY_NAME}' does NOT exist in model '{_mdl}'!")
        print(f"Skipping {BODY_NAME} gracefully to prevent UI freeze.")
        return
"""
    
    new_content = re.sub(safeguard_regex, graceful_safeguard, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(fpath, "w") as f:
            f.write(new_content)
        print(f"Fixed safeguard to return gracefully in {os.path.basename(fpath)}")
