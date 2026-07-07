import glob

files = glob.glob("/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates/*.py")

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    # Search for the mesh_model assignment
    # Usually:
    #     mesh_model = next((m for m in _all_mdls if m != MODEL and
    #                        ("_SM" in m or m.endswith(".gda"))), None)
    # We want to add:
    #     if not mesh_model: mesh_model = MODEL
    
    if "mesh_model =" in content and "if not mesh_model: mesh_model = MODEL" not in content:
        # We can just replace 'None)' with 'MODEL)' in the next() call, OR just append the if statement.
        # Let's replace:
        content = content.replace('("_SM" in m or m.endswith(".gda"))), None)', '("_SM" in m or m.endswith(".gda"))), MODEL)')
        # Some scripts might have: '("_SM" in m or m.endswith(".gda"))), None)' with _all_mdls
        
        # Also check if mesh_EPS.py has it? No, mesh_EPS.py didn't use mesh_model, it just used MODEL.
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed {filepath}")

