#***************************************************************
#SimLab Version 2025.1 
#Created at Fri Jul 10 06:41:04 2026
#***************************************************************
from hwx import simlab

UnitSystem=''' <UnitSystem UUID="3aca8564-4d38-4b0b-887c-6a542d4001c6">
  <SetCurrentDisplaySystem Name="MMKS (mm kg N C s)"/>
 </UnitSystem>''';
simlab.execute(UnitSystem);

CreateSolidBolt=''' <HexBolt UUID="17e5a77d-8b12-4228-bae9-59fc362fefaf" pixmap="hexbolt">
  <tag Value="-1"/>
  <Pattern Name="Pattern3" pixmap=":/images/Hex_Type1.png" type="group">
   <Name Value="Hex1" key="NAME" visible="false"/>
   <ElementType Index="1" Value="Tet" key="ELEMTYPE" type="enum"/>
   <MeshSize Value="2 mm" key="MESHSIZE"/>
   <AngularDivisions Index="1" Value="8" key="ANGULAR_DIV" type="enum"/>
   <Hex_Head Value="0"/>
   <Angle Value="360 deg" key="ANGLE" type="enum"/>
   <P_XYZ Value=" 45.3434 mm,82.5746 mm,14.1514 mm" key="P_X" type="double"/>
   <V_XYZ Value="0 mm,-773.726 mm,0 mm" key="V_X" type="double"/>
   <PivotPointLocation Value="Above Head" key="HEAD_TYP" type="enum"/>
   <InputOption Value="1" key="INPUT_OPTION" name="InputOption" type="enum"/>
   <Washer EntityTypes="" ModelIds="" Value="" key="WASHER_FACES" name="Washer"/>
   <Thread EntityTypes="" ModelIds="" Value="" key="THREAD_FACES" name="Thread"/>
   <WasherGroup EntityTypes="" ModelIds="" Value="" key="WASHER_GRP_FACES" name="WasherGroup"/>
   <ThreadGroup EntityTypes="" ModelIds="" Value="" key="THREAD_GRP_FACES" name="ThreadGroup"/>
   <Shrinkage Value="0.5 mm" name="Shrinkage for inner dia"/>
   <D2Option Value="Shrinkage" expand="true" key="D2_OPTION" name="D2 option" type="group"/>
   <OutputWasher EntityTypes="" ModelIds="" Value="WasherGrp" key="OUTPUT_WASHER_FACES" name="OutputWasher"/>
   <OutputThread EntityTypes="" ModelIds="" Value="ThreadGrp" key="OUTPUT_THREAD_FACES" name="OutputThread"/>
   <OutputPretensionFace EntityTypes="" ModelIds="" Value="PretensionGrp" key="OUTPUT_PRETENSION_FACE" name="OutputPretensionFace"/>
   <BoltImport Value="0"/>
   <ScriptLastChild Value="0"/>
   <Parameters>
    <D1 Value="4 mm"/>
    <D2 Value="3 mm"/>
    <L1 Value="1 mm"/>
    <L2 Value="5 mm"/>
    <L5 Value="5 mm"/>
   </Parameters>
  </Pattern>
 </HexBolt>''';
simlab.execute(CreateSolidBolt);
