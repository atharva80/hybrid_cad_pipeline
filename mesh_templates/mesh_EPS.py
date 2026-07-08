from hwx import simlab

def run(BODY_NAME, config):
    def _v(key, default=None):
        val = config.get(key)
        return val if val is not None else default

    print("=" * 60)
    print(f"  {BODY_NAME} — Complete Mesh Workflow (Atomic)")
    print("=" * 60)

    # -- ROBUST BODY CHECK --
    _all_mdls = simlab.getAllRootModelNames("all")
    _actual_cad = "$Geometry"
    if _all_mdls:
        for m in _all_mdls:
            if not m.endswith(".gda") and "_SM" not in m:
                _actual_cad = m
                break
    _mdl = _actual_cad if "MODEL" not in locals() else MODEL
    if _mdl == "$Geometry" and _actual_cad != "$Geometry":
        _mdl = _actual_cad
        
    _check_bods = simlab.getBodiesWithSubString(_mdl, [BODY_NAME])
    if not _check_bods:
        print(f"WARNING: Body '{BODY_NAME}' does NOT exist in model '{_mdl}'!")
        print(f"Skipping {BODY_NAME} gracefully to prevent UI freeze.")
        return


    UnitSystem=''' <UnitSystem UUID="3aca8564-4d38-4b0b-887c-6a542d4001c6">
  <SetCurrentDisplaySystem Name="MMKS (mm kg N C s)"/>
 </UnitSystem>'''
    simlab.execute(UnitSystem)

    mesh_type = _v('global.mesh_type', 'Tet4')
    tet_type = "Tet4" if mesh_type == "Tet4" else "Tet10StraightEdge"
    mesh_size = _v('global.mesh_size', 4.0)

    print(f"\n-- PHASE: Direct Volume Mesh (Atomic / Bypassed Standalone Surface Mesh) ----------------------")
    TetMesh=f''' <TetMesher UUID="83822e68-12bb-43b9-b2ac-77e0b9ea5149">
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
 </TetMesher>'''
    simlab.execute(TetMesh)
    print(f"  OK {mesh_type} direct volume mesh done")

    # Move to root
    all_models = simlab.getAllRootModelNames("all")
    mesh_model = next((m for m in all_models if "_SM" in m or m.endswith(".gda")), None)
    
    if mesh_model:
        simlab.execute(f'''<MoveSubModelBodiesToRootModel UUID="0619e34b-2275-40b0-b479-882d179d560b">
      <BodiesToMove>
       <Entities>
        <Model>{mesh_model}</Model>
        <Body>"{BODY_NAME}",</Body>
       </Entities>
      </BodiesToMove>
     </MoveSubModelBodiesToRootModel>''')
        print(f"  OK {BODY_NAME} moved to root of {mesh_model}")

    print(f"\n============================================================")
    print(f"  {BODY_NAME} complete!")
    print(f"============================================================")
