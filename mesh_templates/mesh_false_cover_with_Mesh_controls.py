#***************************************************************
#SimLab Version 2025.1 
#Created at Fri Jul 10 12:15:35 2026
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
    <Body>"PCB_BRACKET",</Body>
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
  <Fillets MaxValue="1.1 mm" MinValue="0.9 mm" Value="0"/>
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
  <CreateGrp Name="Group_2" Value="1"/>
 </SelectFeatures>''';
simlab.execute(SelectFeatures);

SelectFeatures=''' <SelectFeatures CheckBox="ON" UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E">
  <SupportEntities>
   <Entities>
    <Model>$Geometry</Model>
    <Face>201723,201721,201719,201717,201715,201713,201711,201709,201707,200691,200693,200695,</Face>
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
  <Fillets MaxValue="1.1 mm" MinValue="0.9 mm" Value="0"/>
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
  <CreateGrp Name="Group_3" Value="1"/>
 </SelectFeatures>''';
simlab.execute(SelectFeatures);

MeshControls=''' <MeshControl CheckBox="ON" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" isObject="1">
  <tag Value="-1"/>
  <MeshControlName Value="IsoLine_MeshControl_1"/>
  <MeshControlType Value="IsoLine"/>
  <Entities>
   <Entities>
    <Model>$Geometry</Model>
    <Face>201723,201721,201719,201717,201715,201713,201711,201709,201707,200691,200693,200695,</Face>
   </Entities>
  </Entities>
  <Reverse EntityTypes="" ModelIds="" Value=""/>
  <MeshColor Value="255,206,0,"/>
  <IsoLine>
   <UseAxialSize Value="1"/>
   <AxialSize Value="2 mm"/>
   <AxialNumElems Value="0"/>
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

SelectFeatures=''' <SelectFeatures CheckBox="ON" UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E">
  <SupportEntities>
   <Entities>
    <Model>$Geometry</Model>
    <Body>"PCB_BRACKET",</Body>
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
  <Cylinders MaxValue="1.8 mm" MinValue="1.5 mm" Value="0"/>
  <CylindersAll Value="0"/>
  <FullCylinder Value="0"/>
  <ClosedPartialCylinder Value="0"/>
  <OpenPartialCylinder Value="0"/>
  <Fillets MaxValue="1.1 mm" MinValue="0.9 mm" Value="1"/>
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
  <CreateGrp Name="Group_4" Value="1"/>
 </SelectFeatures>''';
simlab.execute(SelectFeatures);

SelectFeatures=''' <SelectFeatures CheckBox="ON" UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E">
  <SupportEntities>
   <Entities>
    <Model>$Geometry</Model>
    <Face>201659,201657,201655,201653,201603,201587,201585,201583,201581,201579,201515,201511,201509,201507,201425,201417,200471,200467,200461,200455,200447,200435,200427,200181,200157,199641,199623,199489,199843,199789,199719,199717,199715,199481,199713,199711,199709,199707,199705,199703,199701,199699,199697,199695,199693,199691,199687,199685,201317,201315,201313,201309,201303,201301,201299,201295,201293,201291,201257,201255,201145,201143,201141,201105,201103,201101,201099,201097,201095,201093,201091,201089,201087,200493,201085,201083,201081,</Face>
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
  <Cylinders MaxValue="1.8 mm" MinValue="1.5 mm" Value="0"/>
  <CylindersAll Value="0"/>
  <FullCylinder Value="0"/>
  <ClosedPartialCylinder Value="0"/>
  <OpenPartialCylinder Value="0"/>
  <Fillets MaxValue="1.1 mm" MinValue="0.9 mm" Value="1"/>
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
  <CreateGrp Name="Group_5" Value="1"/>
 </SelectFeatures>''';
simlab.execute(SelectFeatures);

MeshControls=''' <MeshControl CheckBox="ON" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" isObject="1">
  <tag Value="-1"/>
  <MeshControlName Value="Fillet_MeshControl_2"/>
  <MeshControlType Value="Fillet"/>
  <Entities>
   <Entities>
    <Model>$Geometry</Model>
    <Face>201659,201657,201655,201653,201603,201587,201585,201583,201581,201579,201515,201511,201509,201507,201425,201417,200471,200467,200461,200455,200447,200435,200427,200181,200157,199641,199623,199489,199843,199789,199719,199717,199715,199481,199713,199711,199709,199707,199705,199703,199701,199699,199697,199695,199693,199691,199687,199685,201317,201315,201313,201309,201303,201301,201299,201295,201293,201291,201257,201255,201145,201143,201141,201105,201103,201101,201099,201097,201095,201093,201091,201089,201087,200493,201085,201083,201081,</Face>
   </Entities>
  </Entities>
  <Reverse EntityTypes="" ModelIds="" Value=""/>
  <MeshColor Value="0,255,0,"/>
  <FilletMeshControl>
   <AvgSizeAlongFilletLength Value="2 mm" Valve="0.0"/>
   <MaxAnglePerElement Value="45 deg"/>
   <MinElemSize Value="0.2 mm"/>
   <NumElems Value="0"/>
   <AspectRatio Value="10"/>
   <MinRadius Value="0 mm"/>
   <MaxRadius Value="0 mm"/>
   <FltOption Value="2"/>
   <FilletFaceType Value="ALL"/>
  </FilletMeshControl>
 </MeshControl>''';
simlab.execute(MeshControls);

MeshControls=''' <MeshControl CheckBox="ON" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" isObject="1">
  <tag Value="-1"/>
  <MeshControlName Value="Fillet_MeshControl_3"/>
  <MeshControlType Value="Fillet"/>
  <Entities>
   <Group>"Group_4",</Group>
  </Entities>
  <Reverse EntityTypes="" ModelIds="" Value=""/>
  <MeshColor Value="255,0,255,"/>
  <FilletMeshControl>
   <AvgSizeAlongFilletLength Value="2 mm" Valve="0.0"/>
   <MaxAnglePerElement Value="45 deg"/>
   <MinElemSize Value="0.2 mm"/>
   <NumElems Value="0"/>
   <AspectRatio Value="10"/>
   <MinRadius Value="0 mm"/>
   <MaxRadius Value="0 mm"/>
   <FltOption Value="2"/>
   <FilletFaceType Value="ALL"/>
  </FilletMeshControl>
 </MeshControl>''';
simlab.execute(MeshControls);

DeleteMeshControl=''' <DeleteMeshControl CheckBox="ON" UUID="c801afc7-a3eb-4dec-8bc1-8ac6382d4c6e">
  <Name Value="Fillet_MeshControl_2"/>
 </DeleteMeshControl>''';
simlab.execute(DeleteMeshControl);

SurfaceMesh=''' <SurfaceMesh UUID="08df0ff6-f369-4003-956c-82781326c876">
  <tag Value="-1"/>
  <SurfaceMeshType Value="Tri"/>
  <SupportEntities>
   <Entities>
    <Model>$Geometry</Model>
    <Body>"PCB_BRACKET",</Body>
   </Entities>
  </SupportEntities>
  <Tri>
   <ElementType Value="Tri3"/>
   <AverageElementSize Checked="1" Value="4 mm"/>
   <MaximumElementSize Checked="0" Value="0 mm"/>
   <MinimumElementSize Value="0.4 mm"/>
   <GradeFactor Value="1.5"/>
   <MaximumAnglePerElement Value="45 deg"/>
   <CurvatureMinimumElementSize Value="2 mm"/>
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
