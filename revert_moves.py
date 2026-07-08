import os, glob, re

template_dir = "/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates"
files = glob.glob(os.path.join(template_dir, "mesh_*.py"))

def replacer(match):
    block = match.group(0)
    
    # Try to find Model and Body tags inside the MoveBody block
    model_match = re.search(r"<Model>(.*?)</Model>", block)
    body_match = re.search(r"<Body>\"?(.*?)\"?,?</Body>", block)
    
    if not model_match or not body_match:
        return block
        
    mesh_model_var = model_match.group(1)
    body_name_var = body_match.group(1)
    
    return f"""simlab.execute(f'''<MoveSubModelBodiesToRootModel UUID="0619e34b-2275-40b0-b479-882d179d560b">
      <BodiesToMove>
       <Entities>
        <Model>{mesh_model_var}</Model>
        <Body>"{body_name_var}",</Body>
       </Entities>
      </BodiesToMove>
     </MoveSubModelBodiesToRootModel>''')"""

for fpath in files:
    with open(fpath, "r") as f:
        content = f.read()
    
    new_content = re.sub(r"simlab\.execute\(f'''<MoveBody.*?MoveBody>'''\)", replacer, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(fpath, "w") as f:
            f.write(new_content)
        print(f"Reverted to MoveSubModelBodiesToRootModel in {os.path.basename(fpath)}")
