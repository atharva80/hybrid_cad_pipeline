import os
import glob
import re

files = glob.glob("/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates/*.py")
files = [f for f in files if "ARCHIEVE" not in f]

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    # Find the pattern:
    #     if mesh_type in ("Tet4", "Tet10"):
    #     tet_type =
    # or
    #     if mesh_type in ("Tet4", "Tet10"):
    #     TetMesh=
    
    # We need to add 4 spaces to everything between "if mesh_type in..." and "elif mesh_type =="
    pattern = r'(    if mesh_type in \("Tet4", "Tet10"\):\n)(.*?)(    elif mesh_type == "Hex":\n)'
    
    def repl(match):
        prefix = match.group(1)
        body = match.group(2)
        suffix = match.group(3)
        
        # indent body by 4 spaces
        new_body = ""
        for line in body.split('\n'):
            if line:
                new_body += "    " + line + "\n"
            else:
                new_body += "\n"
                
        return prefix + new_body + suffix
        
    new_content = re.sub(pattern, repl, content, flags=re.DOTALL)
    
    # Fix the missing {} around MinimumElementSize Value="size*0.1:.3f mm"
    # Actually it might look like Value="size*0.1:.3f mm" instead of Value="{size*0.1:.3f} mm"
    new_content = re.sub(r'Value="([^"{]+)\*0\.1:\.3f mm"', r'Value="{\1*0.1:.3f} mm"', new_content)
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Fixed {filepath}")

