import os, glob, re

template_dir = "/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates"
files = glob.glob(os.path.join(template_dir, "mesh_*.py"))

safeguard_code = """
    # STRICT PRE-CHECK: Verify Body Exists to prevent C++ API Freezes
    try:
        all_bods = simlab.getBodiesWithSubString(MODEL, [""])
        if not all_bods or BODY_NAME not in all_bods:
            print(f"CRITICAL ERROR: Body '{BODY_NAME}' does NOT exist in model '{MODEL}'.")
            print(f"Available bodies in '{MODEL}': {all_bods[:10] if all_bods else []} ... (truncated)")
            raise RuntimeError(f"Body {BODY_NAME} missing. Pipeline stopped to prevent UI freeze.")
    except Exception as e:
        print(f"Exception during body validation: {e}")
        return
"""

for fpath in files:
    if "mesh_stator.py" in fpath:
        continue # Already updated manually

    with open(fpath, "r") as f:
        content = f.read()
    
    # We want to insert it right after the header block.
    # The header block usually ends with print("=" * 60). We find the first occurrence after MODEL is defined.
    # A safer way is to just look for `print("=" * 60)` which closes the header.
    
    # We find the second `print("=" * 60)` in the file.
    parts = content.split('print("=" * 60)')
    if len(parts) >= 3:
        # Reconstruct with safeguard inserted after the second print("=" * 60)
        new_content = parts[0] + 'print("=" * 60)' + parts[1] + 'print("=" * 60)' + safeguard_code + 'print("=" * 60)'.join(parts[2:])
        if new_content != content:
            with open(fpath, "w") as f:
                f.write(new_content)
            print(f"Added safeguard to {os.path.basename(fpath)}")
