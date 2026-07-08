from hwx import simlab

def run(BODY_NAME, config):
    def _v(key, default=None):
        val = config.get(key)
        return val if val is not None else default

    print("=" * 60)
    print(f"  {BODY_NAME} — Complete Mesh Workflow")
    print("=" * 60)

    UnitSystem=''' <UnitSystem UUID="3aca8564-4d38-4b0b-887c-6a542d4001c6">
  <SetCurrentDisplaySystem Name="MMKS (mm kg N C s)"/>
 </UnitSystem>'''
    simlab.execute(UnitSystem)

    # Resolve MODEL
    models = simlab.getAllRootModelNames("all")
    _all_mdls = simlab.getAllRootModelNames("all")
    MODEL = "$Geometry"
    if _all_mdls:
        for m in _all_mdls:
            if not m.endswith(".gda") and "_SM" not in m:
                MODEL = m
                break
    if models:
        for m in models:
            if m.endswith(".gda") or "_SM" in m:
                MODEL = m
                break
        else:
            MODEL = models[0]

    mesh_type = _v('global.mesh_type', 'Hex')
    # Force Hex for boxes
    mesh_type = 'Hex'
    
    mesh_size = _v('global.mesh_size', 4.0)
    vol_mesh_size = _v('global.vol_mesh_size', 4.0)

    print(f"\n-- PHASE 2: Direct Volume Mesh (Hex / Bypassed Standalone Surface Mesh) ----------------------")
    simlab.execute(f''' <AutoHexMesh UUID="f4ce8a5e-4df8-42de-ab98-547a83e9d7c2">
      <InputBodies>
       <Entities>
        <Model>$Geometry</Model>
        <Body>"{BODY_NAME}",</Body>
       </Entities>
      </InputBodies>
      <AverageElementSize Value="{vol_mesh_size} mm"/>
      <MinimumElementSize Value="{vol_mesh_size*0.1:.3f} mm"/>
      <AllowQuadMeshTransition Checked="0"/>
      <CreateMeshInNewModel Checked="1"/>
      <CreateRingAlongCircleAndSlot Checked="1"/>
      <AvoidSpiderWedgeAlongAxis Checked="0"/>
     </AutoHexMesh>''')
    print(f"  OK Hex volume mesh done")

    # Get mesh model dynamically
    all_models = simlab.getAllRootModelNames("all")
    mesh_model = next((m for m in all_models if "_SM" in m or m.endswith(".gda")), None)

    if mesh_model:
        print(f"\n-- PHASE 5: Move to Root -----------------------------------")
        simlab.execute(f'''<MoveSubModelBodiesToRootModel UUID="0619e34b-2275-40b0-b479-882d179d560b">
          <BodiesToMove><Entities><Model>{mesh_model}</Model><Body>"{BODY_NAME}",</Body></Entities></BodiesToMove>
         </MoveSubModelBodiesToRootModel>''')
        print(f"  OK {BODY_NAME} moved to root of {mesh_model}")
    
    print(f"\n============================================================")
    print(f"  {BODY_NAME} complete!")
    print(f"============================================================")
