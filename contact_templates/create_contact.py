from hwx import simlab

def run(BODY_NAME, config):
    """
    BODY_NAME acts as the Contact Name (e.g., 'SHAFT_STATOR').
    config should contain:
      - master: Name of the master body (e.g., 'SHAFT')
      - slave: Name of the slave body (e.g., 'STATOR')
      - tolerance: Contact tolerance in mm (default 0.3)
      - friction: Coulomb friction coefficient
      - solver: "Radioss", "OptiStruct", etc.
      - contact_type: "Friction (Type24)", etc.
    """
    master = config.get("master")
    slave = config.get("slave")
    tolerance = config.get("tolerance", 0.3)
    friction = config.get("friction", 0.1)
    solver = config.get("solver", "Radioss")

    if not master or not slave:
        print(f"ERROR: Missing master or slave for contact '{BODY_NAME}'")
        return

    print("=" * 60)
    print(f"  Creating Contact: {BODY_NAME}")
    print(f"  Master: {master} | Slave: {slave} | Tol: {tolerance}mm | Fric: {friction}")
    print("=" * 60)

    models = simlab.getAllRootModelNames("all")
    MODEL = "$Geometry"
    if models:
        # Prefer the meshed model (.gda or _SM)
        for m in models:
            if m.endswith(".gda") or "_SM" in m:
                MODEL = m
                break
        else:
            MODEL = models[0]

    DefineManualContact=f''' <Contact BCType="Contact" CheckBox="ON" UUID="3b4a24b5-6aea-49d3-b74a-82bf5b3ec193" customselection="1" isObject="2" pixmap="sizemeshcontrol">
  <tag Value="-1"/>
  <Name Value="{BODY_NAME}"/>
  <New Value="1"/>
  <Entity Index="0" Value="Face"/>
  <MasterEntity>
   <Entities>
    <Model>{MODEL}</Model>
    <Body>"{master}",</Body>
   </Entities>
  </MasterEntity>
  <SlaveEntity>
   <Entities>
    <Model>{MODEL}</Model>
    <Body>"{slave}",</Body>
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
  <Tolerance Value="{tolerance} mm"/>
  <UserContactName Value="0" value=""/>
  <SolverStackIndex Value="{solver}"/>
  <Export Value="0"/>
  <FileName Value=""/>
  <AutoContact Value="0"/>
'''
    contact_type = config.get("contact_type", "Friction (Type 24)")
    type_val = "Type2" if "Type 2" in contact_type or "Tied" in contact_type else "Type24"
    
    DefineManualContact += f'''  <RadiossExplicitContact>
   <RadiossExplicitContactType Value="{type_val}"/>
   <Type24Parameters>
    <StiffnessFactor Value=""/>
    <CoulombFrictionCoefficient Value="{friction if type_val == 'Type24' else ''}"/>
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
 </Contact>'''
    
    try:
        simlab.execute(DefineManualContact)
        print(f"  OK Contact '{BODY_NAME}' created successfully.")
    except Exception as e:
        print(f"  FAILED to create contact '{BODY_NAME}': {e}")
