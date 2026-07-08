import os, glob, re

template_dir = "/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates"
files = glob.glob(os.path.join(template_dir, "mesh_*.py"))

def replacer(match):
    block = match.group(0)
    return block.replace('<CreateNewMeshModel Checked="1"/>', '<CreateNewMeshModel Checked="0"/>')

for fpath in files:
    with open(fpath, "r") as f:
        content = f.read()
    
    new_content = re.sub(r"<SurfaceMesh.*?</SurfaceMesh>", replacer, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(fpath, "w") as f:
            f.write(new_content)
        print(f"Reverted SurfaceMesh in {os.path.basename(fpath)}")
