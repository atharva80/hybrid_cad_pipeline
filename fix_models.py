import glob
import re

files = glob.glob("/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates/*.py")

dynamic_model = """    _all_mdls = simlab.getAllRootModelNames("all")
    MODEL = "$Geometry"
    if _all_mdls:
        for m in _all_mdls:
            if not m.endswith(".gda") and "_SM" not in m:
                MODEL = m
                break"""

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    # Search for MODEL = "$Geometry"
    if 'MODEL = "$Geometry"' in content and '_all_mdls' not in content:
        # replace the first occurrence
        content = content.replace('    MODEL = "$Geometry"', dynamic_model, 1)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed {filepath}")

