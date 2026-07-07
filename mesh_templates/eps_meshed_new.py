#***************************************************************
#SimLab Version 2025.1 
#Created at Tue Jul  7 18:15:34 2026
#***************************************************************
from hwx import simlab

UnitSystem=''' <UnitSystem UUID="3aca8564-4d38-4b0b-887c-6a542d4001c6">
  <SetCurrentDisplaySystem Name="MMKS (mm kg N C s)"/>
 </UnitSystem>''';
simlab.execute(UnitSystem);

TetMesh=''' <TetMesher UUID="83822e68-12bb-43b9-b2ac-77e0b9ea5149">
  <tag Value="-1"/>
  <Name Value="TetMesher1"/>
  <SupportEntities>
   <Entities>
    <Model>$Geometry</Model>
    <Body>"EPS_PACKAGING_2",</Body>
   </Entities>
  </SupportEntities>
  <MeshType Value="Tet4"/>
  <AverageElemSize Value="4 mm"/>
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
   <AverageElementSize Checked="1" Value="4 mm"/>
   <MaximumElementSize Checked="0" Value="5.656 mm"/>
   <MinimumElementSize Value="0.4 mm"/>
   <GradeFactor Value="1.5"/>
   <MaximumAnglePerElement Value="45 deg"/>
   <CurvatureMinimumElementSize Value="2 mm"/>
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
 </TetMesher>''';
simlab.execute(TetMesh);
