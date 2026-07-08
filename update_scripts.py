import os

BOX_TEMPLATE = '''from hwx import simlab

def run(BODY_NAME, config):
    def _v(key, default=None):
        val = config.get(key)
        return val if val is not None else default

    print("=" * 60)
    print(f"  {BODY_NAME} — Complete Mesh Workflow")
    print("=" * 60)

    UnitSystem=\'\'\' <UnitSystem UUID="3aca8564-4d38-4b0b-887c-6a542d4001c6">
  <SetCurrentDisplaySystem Name="MMKS (mm kg N C s)"/>
 </UnitSystem>\'\'\'
    simlab.execute(UnitSystem)

    mesh_size = _v('global.mesh_size', 4.0)
    vol_mesh_size = _v('global.vol_mesh_size', 4.0)
    
    # We will just strictly use the HexMesh since it's a box
    HexMesh=f\'\'\' <AutoHexMesh UUID="f4ce8a5e-4df8-42de-ab98-547a83e9d7c2">
      <InputBodies>
       <Entities>
        <Model>$Geometry</Model>
        <Body>"{BODY_NAME}",</Body>
       </Entities>
      </InputBodies>
      <AverageElementSize Value="{vol_mesh_size} mm"/>
      <MinimumElementSize Value="{vol_mesh_size*0.1:.3f} mm"/>
      <AllowQuadMeshTransition Checked="0"/>
      <CreateMeshInNewModel Checked="0"/>
      <CreateRingAlongCircleAndSlot Checked="1"/>
      <AvoidSpiderWedgeAlongAxis Checked="0"/>
     </AutoHexMesh>\'\'\'
    simlab.execute(HexMesh)
    print(f"  OK Hex volume mesh done")

    # Move to root
    all_models = simlab.getAllRootModelNames("all")
    mesh_model = next((m for m in all_models if "_SM" in m or m.endswith(".gda")), None)
    if mesh_model:
        simlab.execute(f\'\'\'<MoveSubModelBodiesToRootModel UUID="0619e34b-2275-40b0-b479-882d179d560b">
          <BodiesToMove><Entities><Model>{mesh_model}</Model><Body>"{BODY_NAME}",</Body></Entities></BodiesToMove>
         </MoveSubModelBodiesToRootModel>\'\'\')
        print(f"  OK {BODY_NAME} moved to root of {mesh_model}")
        
    print(f"\\n============================================================")
    print(f"  {BODY_NAME} complete!")
    print(f"============================================================")
'''

TET_TEMPLATE = '''from hwx import simlab

def run(BODY_NAME, config):
    def _v(key, default=None):
        val = config.get(key)
        return val if val is not None else default

    print("=" * 60)
    print(f"  {BODY_NAME} — Complete Mesh Workflow")
    print("=" * 60)

    UnitSystem=\'\'\' <UnitSystem UUID="3aca8564-4d38-4b0b-887c-6a542d4001c6">
  <SetCurrentDisplaySystem Name="MMKS (mm kg N C s)"/>
 </UnitSystem>\'\'\'
    simlab.execute(UnitSystem)

    mesh_type = _v('global.mesh_type', '{DEFAULT_TET}')
    tet_type = "Tet4" if mesh_type == "Tet4" else "Tet10StraightEdge"
    mesh_size = _v('global.mesh_size', 4.0)

    TetMesh=f\'\'\' <TetMesher UUID="83822e68-12bb-43b9-b2ac-77e0b9ea5149">
  <tag Value="-1"/>
  <Name Value="{BODY_NAME}_TetMesh"/>
  <SupportEntities>
   <Entities>
    <Model>$Geometry</Model>
    <Body>"{BODY_NAME}",</Body>
   </Entities>
  </SupportEntities>
  <MeshType Value="{tet_type}"/>
  <AverageElemSize Value="{mesh_size} mm"/>
  <MaxElemSize Checked="0" Value="0"/>
  <InternalGrading Value="2"/>
  <MinQuality Value="0.12"/>
  <LinearQuality Value="2"/>
  <MaxQuality Value="1"/>
  <QuadMinQuality Value="0.001"/>
  <QuadQuality Value="0"/>
  <QuadMaxQuality Value="1"/>
  <CadBody Value="1"/>
  <IdentifyFeaturesAndMesh Checked="0"/>
  <MergeTinyFillets Checked="0"/>
  <CreateMatchingMesh Checked="0"/>
  <TransferMeshcontrolFromCAD Checked="0"/>
  <SurfaceMeshParametersForCADInput>
   <AverageElementSize Checked="1" Value="{mesh_size} mm"/>
   <MaximumElementSize Checked="0" Value="{mesh_size * 1.414:.3f} mm"/>
   <MinimumElementSize Value="{mesh_size * 0.1:.3f} mm"/>
   <GradeFactor Value="1.5"/>
   <MaximumAnglePerElement Value="45 deg"/>
   <CurvatureMinimumElementSize Value="{mesh_size * 0.5:.3f} mm"/>
   <AspectRatio Value="10"/>
   <ImproveSkewAngle Value="None"/>
   <MappedMesh Value="Auto"/>
   <MeshPattern Value="Iso mesh"/>
  </SurfaceMeshParametersForCADInput>
  <AdvancedOptions>
   <MeshDensity Value="0"/>
   <CreateNewMeshModel Checked="0"/>
   <OutputModelName Value=""/>
   <Assembly Value="0"/>
   <MeshAsSingleBody Value="0"/>
   <Retain2DSurfaceBodies Value="0"/>
   <FillCavity Value="1"/>
   <MixedMesh Merge="1" Value="0"/>
   <ImmersedMesh Value="0"/>
   <PreserveFaceMesh Value="0"/>
   <StraightenEdges Checked="1"/>
   <PreserveSurfaceSkew Checked="0" Value="55"/>
  </AdvancedOptions>
 </TetMesher>\'\'\'
    simlab.execute(TetMesh)
    print(f"  OK {mesh_type} direct CAD volume mesh done")

    # Move to root
    all_models = simlab.getAllRootModelNames("all")
    mesh_model = next((m for m in all_models if "_SM" in m or m.endswith(".gda")), None)
    if mesh_model:
        simlab.execute(f\'\'\'<MoveSubModelBodiesToRootModel UUID="0619e34b-2275-40b0-b479-882d179d560b">
          <BodiesToMove><Entities><Model>{mesh_model}</Model><Body>"{BODY_NAME}",</Body></Entities></BodiesToMove>
         </MoveSubModelBodiesToRootModel>\'\'\')
        print(f"  OK {BODY_NAME} moved to root of {mesh_model}")
        
    print(f"\\n============================================================")
    print(f"  {BODY_NAME} complete!")
    print(f"============================================================")
'''

base_dir = "/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates"
with open(os.path.join(base_dir, "mesh_boxes.py"), "w") as f:
    f.write(BOX_TEMPLATE)

with open(os.path.join(base_dir, "mesh_canopies.py"), "w") as f:
    f.write(TET_TEMPLATE.replace("{DEFAULT_TET}", "Tet10"))

with open(os.path.join(base_dir, "mesh_false_cover.py"), "w") as f:
    f.write(TET_TEMPLATE.replace("{DEFAULT_TET}", "Tet4"))

print("Templates updated successfully.")
