import os, re
fpath = "/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates/mesh_top_cover_complete.py"
with open(fpath, "r") as f: content = f.read()

replacement = """simlab.execute(f'''<MoveBody UUID="F626E63F-C532-4d7a-8531-15D1E533F4CE">
  <SupportEntities>
   <Entities>
    <Model>{mesh_model}</Model>
    <Body>"{BODY_NAME}",</Body>
   </Entities>
  </SupportEntities>
  <MoveToModel Value="1"/>
  <ModelName Value="ATLAS_MESH"/>
  <UseExistingModel Checked="1"/>
 </MoveBody>''')"""

content = re.sub(r"simlab\.execute\(f'''<MoveSubModelBodiesToRootModel.*?MoveSubModelBodiesToRootModel>'''\)", replacement, content, flags=re.DOTALL)
with open(fpath, "w") as f: f.write(content)
