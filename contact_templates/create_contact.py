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

    models = simlab.getAllModels()
    MODEL = models[0] if models else "$Geometry"

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
  <RadiossExplicitContact>
   <RadiossExplicitContactType Value="Type24"/>
   <Type24Parameters>
    <StiffnessFactor Value=""/>
    <CoulombFrictionCoefficient Value="{friction}"/>
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
  </RadiossExplicitContact>
 </Contact>'''
    
    try:
        simlab.execute(DefineManualContact)
        print(f"  OK Contact '{BODY_NAME}' created successfully.")
    except Exception as e:
        print(f"  FAILED to create contact '{BODY_NAME}': {e}")
