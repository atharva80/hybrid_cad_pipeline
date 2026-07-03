#***************************************************************
#SimLab Version 2025.1 
#Created at Tue Jun 30 16:49:01 2026
#***************************************************************
from hwx import simlab

UnitSystem=''' <UnitSystem UUID="3aca8564-4d38-4b0b-887c-6a542d4001c6">
  <SetCurrentDisplaySystem Name="MMKS (mm kg N C s)"/>
 </UnitSystem>''';
simlab.execute(UnitSystem);

STEP_Import=''' <STEP_Import CheckBox="ON" Type="STEP" UUID="e88f2fcc-2430-4e47-9455-78b4dea9b064" gda="">
  <FileName HelpStr="File name to be imported." Value="E:/Atomberg/hybrid_cad_pipeline/export/HAMSTER_1.2M_MASTER_BOX_ASSLY_NAMED.step" widget="LineEdit"/>
  <Method Value="Convert to Parasolid"/>
  <BodyName Value="1"/>
  <ReadPartName Value="0"/>
  <SketchWireframe Value="0"/>
  <Groups Value="0"/>
  <Imprint Value="0"/>
  <Facets Value="0"/>
  <AssemblyStructure Value="1"/>
  <SaveGeometryInDatabase Value="1"/>
 </STEP_Import>''';
simlab.execute(STEP_Import);
