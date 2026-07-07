import os
import glob

files = glob.glob("/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates/*.py")
files = [f for f in files if "ARCHIEVE" not in f]

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    if "AutoHexMesh" in content: continue

    # Replace the TetMesher block with an if-else
    tet_start = "    tet_type ="
    if tet_start not in content:
        tet_start = "    TetMesh=f''' <TetMesher"
        if tet_start not in content:
            continue
            
    # We will search for TetMesher block
    import re
    
    # We want to find:
    #     tet_type = ...
    #     simlab.execute(f'''<TetMesher UUID="83822e68-12bb-43b9-b2ac-77e0b9ea5149">
    #       ...
    #      </TetMesher>''')
    # Or similar
    
    # Let's find the start of tet_type and the end of </TetMesher>''')
    match = re.search(r'(    tet_type = [^\n]+\n\s+simlab\.execute\(f\'\'\'<TetMesher.*?</TetMesher>\'\'\'\))', content, flags=re.DOTALL)
    
    if match:
        old_block = match.group(1)
        
        # We need to extract the model and body variables used in SupportEntities
        # usually <Model>{mesh_model}</Model> or <Model>{MODEL}</Model>
        model_match = re.search(r'<Model>([^<]+)</Model>', old_block)
        body_match = re.search(r'<Body>([^<]+)</Body>', old_block)
        
        if model_match and body_match:
            model_var = model_match.group(1)
            body_var = body_match.group(1)
            
            # vol_mesh_size
            vol_match = re.search(r'<AverageElemSize Value="([^"]+) mm"/>', old_block)
            vol_var = vol_match.group(1) if vol_match else "{vol_mesh_size}"
            
            new_block = f"""    if mesh_type in ("Tet4", "Tet10"):
{old_block}
    elif mesh_type == "Hex":
        simlab.execute(f''' <AutoHexMesh UUID="f4ce8a5e-4df8-42de-ab98-547a83e9d7c2">
          <InputBodies>
           <Entities>
            <Model>{model_var}</Model>
            <Body>{body_var}</Body>
           </Entities>
          </InputBodies>
          <AverageElementSize Value="{vol_var} mm"/>
          <MinimumElementSize Value="{{float({vol_var}.strip('{{}}'))*0.1}} mm"/>
          <AllowQuadMeshTransition Checked="0"/>
          <CreateMeshInNewModel Checked="0"/>
          <CreateRingAlongCircleAndSlot Checked="1"/>
          <AvoidSpiderWedgeAlongAxis Checked="0"/>
         </AutoHexMesh>''')"""
            
            # The float logic inside f-string: if vol_var is "{vol_mesh_size}", it becomes "{float(vol_mesh_size)*0.1}". 
            if vol_var.startswith("{") and vol_var.endswith("}"):
                min_size = f"{{{vol_var[1:-1]}*0.1:.3f}}"
            else:
                try:
                    min_size = f"{float(vol_var)*0.1:.3f}"
                except:
                    min_size = "0.4"
                    
            new_block = new_block.replace(f"{{float({vol_var}.strip('{{}}'))*0.1}}", min_size.strip('{}'))
            
            content = content.replace(old_block, new_block)
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Updated {filepath}")
    else:
        # Check for mesh_EPS.py style
        match2 = re.search(r'(    TetMesh=f\'\'\' <TetMesher.*?</TetMesher>\'\'\'\n\s+simlab\.execute\(TetMesh\))', content, flags=re.DOTALL)
        if match2:
            old_block = match2.group(1)
            model_match = re.search(r'<Model>([^<]+)</Model>', old_block)
            body_match = re.search(r'<Body>([^<]+)</Body>', old_block)
            model_var = model_match.group(1) if model_match else "{MODEL}"
            body_var = body_match.group(1) if body_match else '"{BODY_NAME}",'
            
            new_block = f"""    if mesh_type in ("Tet4", "Tet10"):
{old_block}
    elif mesh_type == "Hex":
        HexMesh=f''' <AutoHexMesh UUID="f4ce8a5e-4df8-42de-ab98-547a83e9d7c2">
          <InputBodies>
           <Entities>
            <Model>{model_var}</Model>
            <Body>{body_var}</Body>
           </Entities>
          </InputBodies>
          <AverageElementSize Value="{{vol_mesh_size}} mm"/>
          <MinimumElementSize Value="{{vol_mesh_size*0.1:.3f}} mm"/>
          <AllowQuadMeshTransition Checked="0"/>
          <CreateMeshInNewModel Checked="0"/>
          <CreateRingAlongCircleAndSlot Checked="1"/>
          <AvoidSpiderWedgeAlongAxis Checked="0"/>
         </AutoHexMesh>'''
        simlab.execute(HexMesh)"""
            content = content.replace(old_block, new_block)
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Updated {filepath}")

