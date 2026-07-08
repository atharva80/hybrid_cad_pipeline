import os, glob, re

template_dir = "/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates"
files = glob.glob(os.path.join(template_dir, "mesh_*.py"))

def replacer(match):
    # Extract the mesh_model and body_name arguments
    block = match.group(0)
    
    # Try to find Model and Body tags
    model_match = re.search(r"<Model>(.*?)</Model>", block)
    body_match = re.search(r"<Body>\"?(.*?)\"?,?</Body>", block)
    
    if not model_match or not body_match:
        return block # fallback if regex fails
        
    mesh_model_var = model_match.group(1)
    body_name_var = body_match.group(1)
    
    # In python string formatting, the original code had {mesh_model} and {BODY_NAME} etc.
    # So the regex match will literally contain {mesh_model} and {BODY_NAME}_OUTER etc.
    
    return f"""simlab.execute(f'''<MoveBody UUID="F626E63F-C532-4d7a-8531-15D1E533F4CE">
  <SupportEntities>
   <Entities>
    <Model>{mesh_model_var}</Model>
    <Body>"{body_name_var}",</Body>
   </Entities>
  </SupportEntities>
  <MoveToModel Value="1"/>
  <ModelName Value="ATLAS_MESH"/>
  <UseExistingModel Checked="1"/>
 </MoveBody>''')"""

for fpath in files:
    with open(fpath, "r") as f:
        content = f.read()
    
    new_content = re.sub(r"simlab\.execute\(f'''<MoveSubModelBodiesToRootModel.*?MoveSubModelBodiesToRootModel>'''\)", replacer, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(fpath, "w") as f:
            f.write(new_content)
        print(f"Updated MoveBody in {os.path.basename(fpath)}")
