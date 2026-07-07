#***************************************************************
#SimLab Version 2025.1 
#Created at Fri Jul  3 15:42:29 2026
#***************************************************************
from hwx import simlab

UnitSystem=''' <UnitSystem UUID="3aca8564-4d38-4b0b-887c-6a542d4001c6">
  <SetCurrentDisplaySystem Name="MMKS (mm kg N C s)"/>
 </UnitSystem>''';
simlab.execute(UnitSystem);

DefineManualContact=''' <Contact BCType="Contact" CheckBox="ON" UUID="3b4a24b5-6aea-49d3-b74a-82bf5b3ec193" customselection="1" isObject="2" pixmap="sizemeshcontrol">
  <tag Value="-1"/>
  <Name Value="SHAFT_STATOR_1"/>
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
  <Tolerance Value="0.05 mm"/>
  <UserContactName Value="0" value=""/>
  <SolverStackIndex Value="Radioss"/>
  <Export Value="0"/>
  <FileName Value=""/>
  <AutoContact Value="0"/>
  <RadiossExplicitContact>
   <RadiossExplicitContactType Value="Type2"/>
   <Type24Parameters>
    <StiffnessFactor Value=""/>
    <CoulombFrictionCoefficient Value=""/>
    <InitialPenetration Value=""/>
    <CriticalDamping Value=""/>
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
    <TimeDurationForInitPenetration Value=""/>
    <FrictionFilter Value=""/>
    <FilteringCoeff Value=""/>
    <FrictionFormulation Value=""/>
    <FrictionCoefficients c1="" c2="" c3="" c4="" c5="" c6=""/>
    <TimeHistory Value=""/>
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
    <IgnoreSlaveNodes Index="1" Value="1"/>
    <SpotWeldForm Index="0" Value="Default"/>
    <HierarchyLevel Value=""/>
    <SearchForm Index="0" Value="Default"/>
    <NodeDeletion Index="0" Value="Default"/>
    <SearchDist Value=""/>
    <StiffnessFactor Value=""/>
    <CriticalDamping Value=""/>
    <InterfaceStiffness Index="0" Value="Default"/>
    <TimeHistory Value="0"/>
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
