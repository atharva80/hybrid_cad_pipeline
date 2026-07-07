#***************************************************************
#SimLab Version 2025.1 
#Created at Tue Jul  7 15:40:39 2026
#***************************************************************
from hwx import simlab

UnitSystem=''' <UnitSystem UUID="3aca8564-4d38-4b0b-887c-6a542d4001c6">
  <SetCurrentDisplaySystem Name="MMKS (mm kg N C s)"/>
 </UnitSystem>''';
simlab.execute(UnitSystem);

AutoHexMesh=''' <AutoHexMesh UUID="f4ce8a5e-4df8-42de-ab98-547a83e9d7c2">
  <InputBodies>
   <Entities>
    <Model>$Geometry</Model>
    <Body>"Boss-Extrude1",</Body>
    <BodyIndex>17,</BodyIndex>
   </Entities>
  </InputBodies>
  <AverageElementSize Value="4 mm"/>
  <MinimumElementSize Value="0.4 mm"/>
  <AllowQuadMeshTransition Checked="0"/>
  <CreateMeshInNewModel Checked="0"/>
  <CreateRingAlongCircleAndSlot Checked="1"/>
  <AvoidSpiderWedgeAlongAxis Checked="0"/>
 </AutoHexMesh>''';
simlab.execute(AutoHexMesh);

AutoHexMesh=''' <AutoHexMesh UUID="f4ce8a5e-4df8-42de-ab98-547a83e9d7c2">
  <InputBodies>
   <Entities>
    <Model>$Geometry</Model>
    <Body>"Boss-Extrude1",</Body>
    <BodyIndex>17,</BodyIndex>
   </Entities>
  </InputBodies>
  <AverageElementSize Value="4 mm"/>
  <MinimumElementSize Value="0.4 mm"/>
  <AllowQuadMeshTransition Checked="0"/>
  <CreateMeshInNewModel Checked="0"/>
  <CreateRingAlongCircleAndSlot Checked="1"/>
  <AvoidSpiderWedgeAlongAxis Checked="0"/>
 </AutoHexMesh>''';
simlab.execute(AutoHexMesh);
