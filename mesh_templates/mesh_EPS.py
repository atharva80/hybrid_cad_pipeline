from hwx import simlab

def run(BODY_NAME, config):
    def _v(key, default=None):
        val = config.get(key)
        return val if val is not None else default

    print("=" * 60)
    print(f"  {BODY_NAME} — Complete Mesh Workflow")
    print("=" * 60)

    models = simlab.getAllModels()
    MODEL = models[0] if models else "$Geometry"

    mesh_size = _v('global.mesh_size', 6.0)
    vol_mesh_size = _v('global.vol_mesh_size', 7.0)
    mesh_type = _v('global.mesh_type', 'Tet4')
    
    aspect_ratio_limit = _v('quality.aspect_ratio_limit', 10.0)
    min_element_size = _v('quality.min_element_size', 0.6)
    max_angle_per_element = _v('quality.max_angle_per_element', 45.0)
    internal_grading = _v('volume.internal_grading', 2)

    UnitSystem=''' <UnitSystem UUID="3aca8564-4d38-4b0b-887c-6a542d4001c6">
  <SetCurrentDisplaySystem Name="MMKS (mm kg N C s)"/>
 </UnitSystem>'''
    simlab.execute(UnitSystem)

    SurfaceMesh=f''' <SurfaceMesh UUID="08df0ff6-f369-4003-956c-82781326c876">
  <tag Value="-1"/>
  <SurfaceMeshType Value="Tri"/>
  <SupportEntities>
   <Entities>
    <Model>{MODEL}</Model>
    <Body>"{BODY_NAME}",</Body>
   </Entities>
  </SupportEntities>
  <Tri>
   <ElementType Value="Tri3"/>
   <AverageElementSize Checked="1" Value="{mesh_size} mm"/>
   <MaximumElementSize Checked="0" Value="8.484 mm"/>
   <MinimumElementSize Value="{min_element_size} mm"/>
   <GradeFactor Value="1.5"/>
   <MaximumAnglePerElement Value="{max_angle_per_element} deg"/>
   <CurvatureMinimumElementSize Value="3 mm"/>
   <AspectRatio Value="{aspect_ratio_limit}"/>
   <IdentifyFeaturesAndMesh Checked="1"/>
   <MergeTinyFillets Checked="1"/>
   <CreateMatchingMesh Checked="0"/>
   <AdvancedOptions>
    <ImprintMeshing Checked="0"/>
    <Jacobian Checked="0" Value="0.5"/>
    <RemoveFloatingVertices Checked="0" Value="135.0"/>
    <BetterGeometryApproximation Checked="0"/>
    <CoarseMesh Checked="0"/>
    <CoarseMesh_UseExistingNodes Checked="0"/>
    <CreateNewMeshModel Checked="0"/>
    <UserDefinedModelName Value=""/>
    <Tri6WithStraightEdges Checked="0"/>
    <SkipIntersectionCleanup Checked="0"/>
    <ImproveSkewAngle Value="0"/>
    <MappedMesh Value="0"/>
    <MeshPattern Value="0"/>
   </AdvancedOptions>
  </Tri>
 </SurfaceMesh>'''
    simlab.execute(SurfaceMesh)

    TetMesh=f''' <TetMesher UUID="83822e68-12bb-43b9-b2ac-77e0b9ea5149">
  <tag Value="-1"/>
  <Name Value="TetMesher1"/>
  <SupportEntities>
   <Entities>
    <Model>{MODEL}</Model>
    <Body>"{BODY_NAME}",</Body>
   </Entities>
  </SupportEntities>
  <MeshType Value="{mesh_type}"/>
  <AverageElemSize Value="{vol_mesh_size} mm"/>
  <MaxElemSize Checked="0" Value="0"/>
  <InternalGrading Value="{internal_grading}"/>
  <MinQuality Value="0.12"/>
  <LinearQuality Value="2"/>
  <MaxQuality Value="1"/>
  <QuadMinQuality Value="0.001"/>
  <QuadQuality Value="0"/>
  <QuadMaxQuality Value="1"/>
  <CadBody Value="0"/>
  <IdentifyFeaturesAndMesh Checked="0"/>
  <MergeTinyFillets Checked="0"/>
  <CreateMatchingMesh Checked="0"/>
  <TransferMeshcontrolFromCAD Checked="0"/>
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

