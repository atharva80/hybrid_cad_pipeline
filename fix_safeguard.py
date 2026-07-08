import os, glob, re

template_dir = "/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates"
files = glob.glob(os.path.join(template_dir, "mesh_*.py"))

for fpath in files:
    with open(fpath, "r") as f:
        content = f.read()

    # Find the flawed safeguard block
    safeguard_regex = r"    # STRICT PRE-CHECK.*?return\n"
    
    # We replace it with a robust check
    robust_safeguard = """
    # -- ROBUST BODY CHECK --
    _mdl = "$Geometry" if "MODEL" not in locals() else MODEL
    _check_bods = simlab.getBodiesWithSubString(_mdl, [BODY_NAME])
    if not _check_bods:
        print(f"CRITICAL ERROR: Body '{BODY_NAME}' does NOT exist in model '{_mdl}'!")
        raise RuntimeError(f"Body {BODY_NAME} missing. Halting to prevent freeze.")
"""
    
    new_content = re.sub(safeguard_regex, robust_safeguard, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(fpath, "w") as f:
            f.write(new_content)
        print(f"Fixed safeguard in {os.path.basename(fpath)}")
