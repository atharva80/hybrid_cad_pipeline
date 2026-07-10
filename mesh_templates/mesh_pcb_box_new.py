#***************************************************************
#SimLab Version 2025.1 
#Created at Thu Jul  9 15:54:12 2026
#***************************************************************
from hwx import simlab

UnitSystem=''' <UnitSystem UUID="3aca8564-4d38-4b0b-887c-6a542d4001c6">
  <SetCurrentDisplaySystem Name="MMKS (mm kg N C s)"/>
 </UnitSystem>''';
simlab.execute(UnitSystem);

SelectFeatures=''' <SelectFeatures CheckBox="ON" UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E">
  <SupportEntities>
   <Entities>
    <Model>$Geometry</Model>
    <Body>"PCB_BOX",</Body>
   </Entities>
  </SupportEntities>
  <Arcs MaxValue="7.8 mm" MinValue="7.5 mm" Value="0"/>
  <ArcsAll Value="0"/>
  <Circles MaxValue="8 mm" MinValue="0 mm" Value="0"/>
  <CirclesAll Value="0"/>
  <Cones MaxValue="8 mm" MinValue="7 mm" Value="1"/>
  <ConeAll Value="0"/>
  <FullCone Value="1"/>
  <ClosedPartialCone Value="1"/>
  <OpenPartialCone Value="0"/>
  <TaperAngle Angle="0 deg" Value="0"/>
  <Dics MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <DicsAll Value="0"/>
  <HollowDics MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <HollowDicsAll Value="0"/>
  <Cylinders MaxValue="8 mm" MinValue="7 mm" Value="0"/>
  <CylindersAll Value="0"/>
  <FullCylinder Value="0"/>
  <ClosedPartialCylinder Value="0"/>
  <OpenPartialCylinder Value="0"/>
  <Fillets MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <FilletsOption Value="1"/>
  <PlanarFaces Value="0"/>
  <FourEdgedFaces Value="0"/>
  <ConnectedCoaxialFaces Value="0"/>
  <ThroughBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHoleDepth MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <SlotEdges MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <SlotEdgesAll Value="0"/>
  <ArcLengthBased Value=""/>
  <AngleBased Value=""/>
  <SharpEdges Angle="" Option="" Value=""/>
  <ThicknessBased Value=""/>
  <LogosAndDetails Value=""/>
  <LogosAndDetailsThickness Value=""/>
  <CreateGrp Name="Group_1" Value="0"/>
 </SelectFeatures>''';
simlab.execute(SelectFeatures);

SelectFeatures=''' <SelectFeatures CheckBox="ON" UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E">
  <SupportEntities>
   <Entities>
    <Model>$Geometry</Model>
    <Face>425159,425155,425157,425113,425109,425111,424489,424721,424611,424423,425091,425093,</Face>
   </Entities>
  </SupportEntities>
  <Arcs MaxValue="7.8 mm" MinValue="7.5 mm" Value="0"/>
  <ArcsAll Value="0"/>
  <Circles MaxValue="8 mm" MinValue="0 mm" Value="0"/>
  <CirclesAll Value="0"/>
  <Cones MaxValue="8 mm" MinValue="7 mm" Value="1"/>
  <ConeAll Value="0"/>
  <FullCone Value="1"/>
  <ClosedPartialCone Value="1"/>
  <OpenPartialCone Value="0"/>
  <TaperAngle Angle="0 deg" Value="0"/>
  <Dics MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <DicsAll Value="0"/>
  <HollowDics MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <HollowDicsAll Value="0"/>
  <Cylinders MaxValue="8 mm" MinValue="7 mm" Value="0"/>
  <CylindersAll Value="0"/>
  <FullCylinder Value="0"/>
  <ClosedPartialCylinder Value="0"/>
  <OpenPartialCylinder Value="0"/>
  <Fillets MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <FilletsOption Value="1"/>
  <PlanarFaces Value="0"/>
  <FourEdgedFaces Value="0"/>
  <ConnectedCoaxialFaces Value="0"/>
  <ThroughBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHoleDepth MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <SlotEdges MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <SlotEdgesAll Value="0"/>
  <ArcLengthBased Value=""/>
  <AngleBased Value=""/>
  <SharpEdges Angle="" Option="" Value=""/>
  <ThicknessBased Value=""/>
  <LogosAndDetails Value=""/>
  <LogosAndDetailsThickness Value=""/>
  <CreateGrp Name="Group_1" Value="0"/>
 </SelectFeatures>''';
simlab.execute(SelectFeatures);

MeshControls=''' <MeshControl CheckBox="ON" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" isObject="1">
  <tag Value="-1"/>
  <MeshControlName Value="IsoLine_MeshControl_18"/>
  <MeshControlType Value="IsoLine"/>
  <Entities>
   <Entities>
    <Model>$Geometry</Model>
    <Face>425159,425155,425157,425113,425109,425111,424489,424721,424611,424423,425091,425093,</Face>
   </Entities>
  </Entities>
  <Reverse EntityTypes="" ModelIds="" Value=""/>
  <MeshColor Value="255,206,0,"/>
  <IsoLine>
   <UseAxialSize Value="1"/>
   <AxialSize Value="3 mm"/>
   <AxialNumElems Value="0"/>
   <UseCirAngle Value="0"/>
   <CirAngle Value="0 deg"/>
   <CirNumElems Value="16"/>
   <AspectRatio Value="10"/>
   <MinElemSize Value="0 mm"/>
   <MergeFaces Value="1"/>
   <CreateUniformMesh Value="0"/>
   <StartPointPicked Value="0"/>
   <CentreX Value="0 mm"/>
   <CentreY Value="0 mm"/>
   <CentreZ Value="0 mm"/>
   <RevDirection Value="0"/>
   <ExtendLayers Value="0"/>
   <AlignStartPointToLocalAxis Value="0"/>
  </IsoLine>
 </MeshControl>''';
simlab.execute(MeshControls);

SelectFeatures=''' <SelectFeatures CheckBox="ON" UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E">
  <SupportEntities>
   <Entities>
    <Model>$Geometry</Model>
    <Body>"PCB_BOX",</Body>
   </Entities>
  </SupportEntities>
  <Arcs MaxValue="7.8 mm" MinValue="7.5 mm" Value="0"/>
  <ArcsAll Value="0"/>
  <Circles MaxValue="8 mm" MinValue="0 mm" Value="0"/>
  <CirclesAll Value="0"/>
  <Cones MaxValue="8 mm" MinValue="7 mm" Value="0"/>
  <ConeAll Value="0"/>
  <FullCone Value="0"/>
  <ClosedPartialCone Value="0"/>
  <OpenPartialCone Value="0"/>
  <TaperAngle Angle="0 deg" Value="0"/>
  <Dics MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <DicsAll Value="0"/>
  <HollowDics MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <HollowDicsAll Value="0"/>
  <Cylinders MaxValue="1.8 mm" MinValue="1.5 mm" Value="1"/>
  <CylindersAll Value="0"/>
  <FullCylinder Value="1"/>
  <ClosedPartialCylinder Value="1"/>
  <OpenPartialCylinder Value="1"/>
  <Fillets MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <FilletsOption Value="1"/>
  <PlanarFaces Value="0"/>
  <FourEdgedFaces Value="0"/>
  <ConnectedCoaxialFaces Value="0"/>
  <ThroughBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHoleDepth MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <SlotEdges MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <SlotEdgesAll Value="0"/>
  <ArcLengthBased Value=""/>
  <AngleBased Value=""/>
  <SharpEdges Angle="" Option="" Value=""/>
  <ThicknessBased Value=""/>
  <LogosAndDetails Value=""/>
  <LogosAndDetailsThickness Value=""/>
  <CreateGrp Name="Group_1" Value="0"/>
 </SelectFeatures>''';
simlab.execute(SelectFeatures);

SelectFeatures=''' <SelectFeatures CheckBox="ON" UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E">
  <SupportEntities>
   <Entities>
    <Model>$Geometry</Model>
    <Face>424431,424429,424425,424469,</Face>
   </Entities>
  </SupportEntities>
  <Arcs MaxValue="7.8 mm" MinValue="7.5 mm" Value="0"/>
  <ArcsAll Value="0"/>
  <Circles MaxValue="8 mm" MinValue="0 mm" Value="0"/>
  <CirclesAll Value="0"/>
  <Cones MaxValue="8 mm" MinValue="7 mm" Value="0"/>
  <ConeAll Value="0"/>
  <FullCone Value="0"/>
  <ClosedPartialCone Value="0"/>
  <OpenPartialCone Value="0"/>
  <TaperAngle Angle="0 deg" Value="0"/>
  <Dics MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <DicsAll Value="0"/>
  <HollowDics MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <HollowDicsAll Value="0"/>
  <Cylinders MaxValue="1.8 mm" MinValue="1.5 mm" Value="1"/>
  <CylindersAll Value="0"/>
  <FullCylinder Value="1"/>
  <ClosedPartialCylinder Value="1"/>
  <OpenPartialCylinder Value="1"/>
  <Fillets MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <FilletsOption Value="1"/>
  <PlanarFaces Value="0"/>
  <FourEdgedFaces Value="0"/>
  <ConnectedCoaxialFaces Value="0"/>
  <ThroughBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHoleDepth MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <SlotEdges MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <SlotEdgesAll Value="0"/>
  <ArcLengthBased Value=""/>
  <AngleBased Value=""/>
  <SharpEdges Angle="" Option="" Value=""/>
  <ThicknessBased Value=""/>
  <LogosAndDetails Value=""/>
  <LogosAndDetailsThickness Value=""/>
  <CreateGrp Name="Group_1" Value="0"/>
 </SelectFeatures>''';
simlab.execute(SelectFeatures);

MeshControls=''' <MeshControl CheckBox="ON" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" isObject="1">
  <tag Value="-1"/>
  <MeshControlName Value="IsoLine_MeshControl_19"/>
  <MeshControlType Value="IsoLine"/>
  <Entities>
   <Entities>
    <Model>$Geometry</Model>
    <Face>424431,424429,424425,424469,</Face>
   </Entities>
  </Entities>
  <Reverse EntityTypes="" ModelIds="" Value=""/>
  <MeshColor Value="0,255,0,"/>
  <IsoLine>
   <UseAxialSize Value="0"/>
   <AxialSize Value="0 mm"/>
   <AxialNumElems Value="2"/>
   <UseCirAngle Value="0"/>
   <CirAngle Value="0 deg"/>
   <CirNumElems Value="8"/>
   <AspectRatio Value="10"/>
   <MinElemSize Value="0 mm"/>
   <MergeFaces Value="1"/>
   <CreateUniformMesh Value="0"/>
   <StartPointPicked Value="0"/>
   <CentreX Value="0 mm"/>
   <CentreY Value="0 mm"/>
   <CentreZ Value="0 mm"/>
   <RevDirection Value="0"/>
   <ExtendLayers Value="0"/>
   <AlignStartPointToLocalAxis Value="0"/>
  </IsoLine>
 </MeshControl>''';
simlab.execute(MeshControls);

SurfaceMesh=''' <SurfaceMesh UUID="08df0ff6-f369-4003-956c-82781326c876">
  <tag Value="-1"/>
  <SurfaceMeshType Value="Tri"/>
  <SupportEntities>
   <Entities>
    <Model>$Geometry</Model>
    <Body>"PCB_BOX",</Body>
   </Entities>
  </SupportEntities>
  <Tri>
   <ElementType Value="Tri3"/>
   <AverageElementSize Checked="1" Value="3 mm"/>
   <MaximumElementSize Checked="0" Value="0 mm"/>
   <MinimumElementSize Value="0.3 mm"/>
   <GradeFactor Value="1.5"/>
   <MaximumAnglePerElement Value="45 deg"/>
   <CurvatureMinimumElementSize Value="1.5 mm"/>
   <AspectRatio Value="10"/>
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
 </SurfaceMesh>''';
simlab.execute(SurfaceMesh);
