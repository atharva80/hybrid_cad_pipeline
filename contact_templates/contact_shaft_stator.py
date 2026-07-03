#***************************************************************
#SimLab Version 2025.1 
#Created at Thu Jul  2 16:06:34 2026
#***************************************************************
from hwx import simlab

UnitSystem=''' <UnitSystem UUID="3aca8564-4d38-4b0b-887c-6a542d4001c6">
  <SetCurrentDisplaySystem Name="MMKS (mm kg N C s)"/>
 </UnitSystem>''';
simlab.execute(UnitSystem);

DefineManualContact=''' <Contact BCType="Contact" CheckBox="ON" UUID="3b4a24b5-6aea-49d3-b74a-82bf5b3ec193" customselection="1" isObject="2" pixmap="sizemeshcontrol">
  <tag Value="-1"/>
  <Name Value="SHAFT_STATOR_2"/>
  <New Value="1"/>
  <Entity Index="0" Value="Face"/>
  <MasterEntity>
   <Entities>
    <Model>prime_named_paratr1_SM.gda</Model>
    <Body>"SHAFT",</Body>
   </Entities>
  </MasterEntity>
  <SlaveEntity>
   <Entities>
    <Model>prime_named_paratr1_SM.gda</Model>
    <Body>"STATOR",</Body>
   </Entities>
  </SlaveEntity>
  <IgnoreEdges/>
  <IgnoreBodies EntityTypes="" ModelIds="" Value=""/>
  <MasterSet Value=""/>
  <SlaveSet Value=""/>
  <ContactBodyPairList/>
  <Trim Value="Secondary and Main"/>
  <SurfaceInteraction Index="0" Value="None"/>
  <PressFit Index="0" Value="None"/>
  <ContactFaceType Value="All"/>
  <Tolerance Value="0.318894 mm"/>
  <UserContactName Value="0" value=""/>
  <SolverStackIndex Value="Radioss"/>
  <Export Value="0"/>
  <FileName Value=""/>
  <AutoContact Value="0"/>
  <RadiossExplicitContact>
   <RadiossExplicitContactType Value="Type24"/>
   <Type24Parameters>
    <StiffnessFactor Value=""/>
    <CoulombFrictionCoefficient Value=""/>
    <InitialPenetration Index="2" Value="Shift main segment by initial penetration"/>
    <CriticalDamping Value=""/>
    <InterfaceStiffness Index="0" Value="Default"/>
    <DeletionFlag Index="0" Value="Default"/>
    <MaxSlaveGap Value=""/>
    <MaxMasterGap Value=""/>
    <MinimumStiffness Value=""/>
    <MaximumStiffness Value=""/>
    <GapModification Index="0" Value="Default"/>
    <InitialPenetrationDetection Index="0" Value="Default"/>
    <MaximumInitPenetration Value=""/>
    <StartTime Value=""/>
    <EndTime Value=""/>
    <DeactivationBC Index="0" Value="False"/>
    <TimeDurationForInitPenetration Value=" "/>
    <FrictionFilter Index="0" Value="Default"/>
    <FilteringCoeff Value=""/>
    <FrictionFormulation Index="0" Value="Static coulomb"/>
    <FrictionCoefficients c1="" c2="" c3="" c4="" c5="" c6=""/>
    <TimeHistory Value="0"/>
   </Type24Parameters>
   <Type25Parameters>
    <StiffnessFactor Value=""/>
    <CoulombFrictionCoefficient Value=""/>
    <InitialPenetration Value=""/>
    <CriticalDamping Value=""/>
    <GapFormulationMethod Value=""/>
    <MeshSizePercentage Value=""/>
    <InterfaceStiffness Value=""/>
    <DeletionFlag Value=""/>
    <MaxSlaveGap Value=""/>
    <MaxMasterGap Value=""/>
    <MinimumStiffness Value=""/>
    <MaximumStiffness Value=""/>
    <GapModification Value=""/>
    <InitialPenetrationDetection Value=""/>
    <MaximumInitPenetration Value=""/>
    <StartTime Value=""/>
    <EndTime Value=""/>
    <DeactivationBC Value=""/>
    <FrictionFilter Value=""/>
    <FilteringCoeff Value=""/>
    <FrictionFormulation Value=""/>
    <FrictionCoefficients c1="" c2="" c3="" c4="" c5="" c6=""/>
    <TimeHistory Value=""/>
   </Type25Parameters>
   <Type2Parameters>
    <IgnoreSlaveNodes Value=""/>
    <SpotWeldForm Value=""/>
    <HierarchyLevel Value=""/>
    <SearchForm Value=""/>
    <NodeDeletion Value=""/>
    <SearchDist Value=""/>
    <StiffnessFactor Value=""/>
    <CriticalDamping Value=""/>
    <InterfaceStiffness Value=""/>
    <TimeHistory Value=""/>
    <SpotWeldAdvanceOption>
     <FailureModel Value=""/>
     <FilterFlag Value=""/>
     <StressFunction Value=""/>
     <NormalFunction Value=""/>
     <TangentialFunction Value=""/>
     <RuptureFlag Value=""/>
     <MaxNormal Value=""/>
     <MaxTangential Value=""/>
     <StressAlpha Value=""/>
     <SurfaceArea Value=""/>
    </SpotWeldAdvanceOption>
   </Type2Parameters>
   <Type7Parameters>
    <InterfaceStiffness Value=""/>
    <CoulombFriction Value=""/>
    <GapFormulationMethod Value=""/>
    <MaximumGap Value=""/>
    <MinimumGap Value=""/>
    <ActivateHeatTrans Value=""/>
    <ActivateVentClosure Value=""/>
    <NodeDeletion Value=""/>
    <GapCurvature Value=""/>
    <LocalCurvature Value=""/>
    <GapScaleFact Value=""/>
    <MaxInitialPenetration Value=""/>
    <MinimumStiffness Value=""/>
    <MaximumStiffness Value=""/>
    <MeshSizePercentage Value=""/>
    <MinNodalTimeStep Value=""/>
    <DeactivateSNElemSize Value=""/>
    <DeactivateSNContactPair Value=""/>
    <StiffScaleFact Value=""/>
    <FilteringCoeffTable Index="" Value=""/>
    <StartTime Value=""/>
    <EndTime Value=""/>
    <DeactivateBoundaryCondition Value=""/>
    <StiffDeactivation Value=""/>
    <CritDampOnStiff Value=""/>
    <CritDampOnFric Value=""/>
    <SortingFact Value=""/>
    <FricPenaltyForm Value=""/>
    <FrictionFilter Value=""/>
    <FilteringCoeff Value=""/>
    <FrictionFormulation Value=""/>
    <FrictionCoefficients c1="" c2="" c3="" c4="" c5="" c6=""/>
    <HeatExchCoeff Value=""/>
    <HeatExchCoeffTable Index="" Value=""/>
    <InterfaceTemp Value=""/>
    <HeatContFormulation Value=""/>
    <PenetrationCriteria Value=""/>
    <AngleCriteria Value=""/>
    <RadiationFactore Value=""/>
    <MaxDisForRadiation Value=""/>
    <MasterFrictHeatFact Value=""/>
    <SlaveFricHeatFact Value=""/>
    <TimeHistory Value=""/>
   </Type7Parameters>
  </RadiossExplicitContact>
 </Contact>''';
simlab.execute(DefineManualContact);
