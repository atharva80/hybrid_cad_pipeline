# -*- coding: utf-8 -*-
# =============================================================================
# SCRIPT  : mesh_bottom_cover.py
# PURPOSE : Complete mesh workflow for BOTTOM_COVER (optional component)
# MESH CONTROLS:
#   1. Logo Removal — ThicknessBased/LogosAndDetails faces
# NOTE: Outer radius = 66.88mm (to be made GUI input later)
# =============================================================================

from hwx import simlab

# -- USER INPUTS ---------------------------------------------------------------
# -----------------------------------------------------------------------------



def run(BODY_NAME, config):
    def _v(key, default=None):
        val = config.get(key)
        return val if val is not None else default

    _all_mdls = simlab.getAllRootModelNames("all")
    MODEL = "$Geometry"
    if _all_mdls:
        for m in _all_mdls:
            if not m.endswith(".gda") and "_SM" not in m:
                MODEL = m
                break
    mesh_size = _v('global.mesh_size', 4.0)
    surf_mesh_size = _v('global.surf_mesh_size', 4.0)
    vol_mesh_size = _v('global.vol_mesh_size', 4.0)
    mesh_type = _v('global.mesh_type', 'Tet4')

    temp_dir = config.get('__temp_dir__', 'C:/temp')
    TARGET_AREA = _v('special.target_area', 527.9)
    TOLERANCE = _v('special.area_tolerance', 10.0)

    print("=" * 60)
    print(f"  BOTTOM_COVER — Complete Mesh Workflow")
    print(f"  Surface: {surf_mesh_size}mm | Volume: {vol_mesh_size}mm | Type: {mesh_type}")
    print("=" * 60)

    # -- ROBUST BODY CHECK --
    _all_mdls = simlab.getAllRootModelNames("all")
    _actual_cad = "$Geometry"
    if _all_mdls:
        for m in _all_mdls:
            if not m.endswith(".gda") and "_SM" not in m:
                _actual_cad = m
                break
    _mdl = _actual_cad if "MODEL" not in locals() else MODEL
    if _mdl == "$Geometry" and _actual_cad != "$Geometry":
        _mdl = _actual_cad
        
    _check_bods = simlab.getBodiesWithSubString(_mdl, [BODY_NAME])
    if not _check_bods:
        print(f"WARNING: Body '{BODY_NAME}' does NOT exist in model '{_mdl}'!")
        print(f"Skipping {BODY_NAME} gracefully to prevent UI freeze.")
        return


    # ===============================================================
    # PHASE 1: MESH CONTROLS
    # ===============================================================
    print("\n-- PHASE 1: Mesh Controls ----------------------------------")

    print(f"\n[MC1] Logo Removal...")
    simlab.execute(f'''<SelectFeatures UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E" CheckBox="ON">
      <SupportEntities><Entities><Model>{MODEL}</Model><Body>"{BODY_NAME}",</Body></Entities></SupportEntities>
      <Arcs MinValue="" MaxValue="" Value=""/><ArcsAll Value=""/>
      <Circles MinValue="" MaxValue="" Value=""/><CirclesAll Value=""/>
      <Cones MinValue="" MaxValue="" Value=""/><ConeAll Value=""/>
      <FullCone Value=""/><ClosedPartialCone Value=""/><OpenPartialCone Value=""/>
      <TaperAngle Angle="" Value=""/>
      <Dics MinValue="" MaxValue="" Value=""/><DicsAll Value=""/>
      <HollowDics MinValue="" MaxValue="" Value=""/><HollowDicsAll Value=""/>
      <Cylinders MinValue="" MaxValue="" Value=""/><CylindersAll Value=""/>
      <FullCylinder Value=""/><ClosedPartialCylinder Value=""/><OpenPartialCylinder Value=""/>
      <Fillets MinValue="" MaxValue="" Value=""/><FilletsOption Value=""/>
      <PlanarFaces Value=""/><FourEdgedFaces Value=""/><ConnectedCoaxialFaces Value=""/>
      <ThroughBoltHole MinValue="" MaxValue="" Value=""/>
      <BlindBoltHole MinValue="" MaxValue="" Value=""/>
      <BlindBoltHoleDepth MinValue="" MaxValue="" Value=""/>
      <SlotEdges MinValue="" MaxValue="" Value=""/><SlotEdgesAll Value=""/>
      <ArcLengthBased Value=""/><AngleBased Value=""/>
      <SharpEdges Angle="" Option="" Value=""/><ThicknessBased Value="1"/>
      <LogosAndDetails Value="1"/><LogosAndDetailsThickness Value="2 mm"/>
      <CreateGrp Value="1" Name="{BODY_NAME}_Logo_Faces"/>
     </SelectFeatures>''')
    logo_faces = simlab.getSelectedEntities("Face")
    print(f"  Logo faces: {len(logo_faces) if logo_faces else 0}")
    if logo_faces:
        simlab.execute(f'''<MeshControl UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" isObject="1" CheckBox="ON">
      <tag Value="-1"/>
      <MeshControlName Value="{BODY_NAME}_LogoRemoval"/>
      <MeshControlType Value="Defeature Logo"/>
      <Entities><Group>"{BODY_NAME}_Logo_Faces",</Group></Entities>
      <Reverse ModelIds="" Value="" EntityTypes=""/>
      <MeshColor Value="255,206,0,"/>
      <RemoveLogo/>
     </MeshControl>''')
        print("  OK Logo Removal MC applied")
    else:
        print("  - No logo faces found")

    # ===============================================================
    # PHASE 2: SURFACE MESH
    # ===============================================================
    print("\n-- PHASE 2: Surface Mesh -----------------------------------")
    simlab.execute(f'''<SurfaceMesh UUID="08df0ff6-f369-4003-956c-82781326c876">
      <tag Value="-1"/>
      <SurfaceMeshType Value="Tri"/>
      <SupportEntities><Entities><Model>{MODEL}</Model><Body>"{BODY_NAME}",</Body></Entities></SupportEntities>
      <Tri>
       <ElementType Value="Tri3"/>
       <AverageElementSize Checked="1" Value="{surf_mesh_size} mm"/>
       <MaximumElementSize Checked="0" Value="{surf_mesh_size*1.414:.3f} mm"/>
       <MinimumElementSize Value="{surf_mesh_size*0.1:.3f} mm"/>
       <GradeFactor Value="1.5"/>
       <MaximumAnglePerElement Value="45 deg"/>
       <CurvatureMinimumElementSize Value="{surf_mesh_size*0.5:.3f} mm"/>
       <AspectRatio Value="10"/><IdentifyFeaturesAndMesh Checked="1"/>
       <MergeTinyFillets Checked="1"/><CreateMatchingMesh Checked="0"/>
       <AdvancedOptions>
        <ImprintMeshing Checked="0"/><Jacobian Checked="0" Value="0.5"/>
        <RemoveFloatingVertices Checked="0" Value="135.0"/>
        <BetterGeometryApproximation Checked="0"/><CoarseMesh Checked="0"/>
        <CoarseMesh_UseExistingNodes Checked="0"/><CreateNewMeshModel Checked="0"/>
        <UserDefinedModelName Value=""/><Tri6WithStraightEdges Checked="0"/>
        <SkipIntersectionCleanup Checked="0"/><ImproveSkewAngle Value="0"/>
        <MappedMesh Value="0"/><MeshPattern Value="0"/>
       </AdvancedOptions>
      </Tri>
     </SurfaceMesh>''')
    print("  OK Surface mesh done")

    all_models = simlab.getAllRootModelNames("all")
    mesh_model = next((m for m in all_models if m != MODEL and
                       ("_SM" in m or m.endswith(".gda"))), MODEL)
    print(f"  Mesh model: {mesh_model}")

    # ===============================================================
    # PHASE 3: QUALITY CHECK + CLEANUP
    # ===============================================================
    print("\n-- PHASE 3: Quality Check + Cleanup ------------------------")
    _ar = _v('quality.aspect_ratio_limit', 10.0)
    _el = _v('quality.min_edge_length', 0.25)
    _ht = _v('quality.min_height', 0.2)
    for opt, cond, name, extra in [
        ("Compute", "G Than Or Eq", "Aspect Ratio", f'LimitValue="{_ar}"'),
        ("Cleanup", "L Than and G Than Or Eq", "Edge Length",
         f'MaximumLimitValue="100 mm" MinimumLimitValue="{_el} mm"'),
        ("Cleanup", "L Than", "Height", f'LimitValue="{_ht} mm"'),
    ]:
        simlab.execute(f'''<QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
      <ElementType Value="Tri"/><Option Value="{opt}"/>
      <Quality Condition="{cond}" {extra} Name="{name}"/>
      <SupportEntities><Entities><Model>{mesh_model}</Model><Body>"{BODY_NAME}",</Body></Entities></SupportEntities>
      <CleanupType Value="Modify Element"/><PreserveSurfaceSkew Check="0" Value="55"/>
     </QCheck>''')
    print("  OK Quality cleanup done")

    # ===============================================================
    # PHASE 4: VOLUME MESH
    # ===============================================================
    print(f"\n-- PHASE 4: Volume Mesh ({mesh_type}) ----------------------")
    if mesh_type in ("Tet4", "Tet10"):
        tet_type = "Tet4" if mesh_type == "Tet4" else "Tet10StraightEdge"
        simlab.execute(f'''<TetMesher UUID="83822e68-12bb-43b9-b2ac-77e0b9ea5149">
          <tag Value="-1"/>
          <Name Value="{BODY_NAME}_TetMesh_{mesh_type}"/>
          <SupportEntities><Entities><Model>{mesh_model}</Model><Body>"{BODY_NAME}",</Body></Entities></SupportEntities>
          <MeshType Value="{tet_type}"/>
          <AverageElemSize Value="{vol_mesh_size} mm"/>
          <MaxElemSize Checked="0" Value="0"/><InternalGrading Value="{int(_v('volume.internal_grading', 2.0))}"/>
          <MinQuality Value="{_v('volume.min_quality', 0.12)}"/><LinearQuality Value="2"/><MaxQuality Value="1"/>
          <QuadMinQuality Value="0.001"/><QuadQuality Value="0"/><QuadMaxQuality Value="1"/>
          <CadBody Value="0"/><IdentifyFeaturesAndMesh Checked="0"/>
          <MergeTinyFillets Checked="0"/><CreateMatchingMesh Checked="0"/>
          <TransferMeshcontrolFromCAD Checked="0"/>
          <AdvancedOptions>
           <MeshDensity Value="0"/><CreateNewMeshModel Checked="0"/>
           <OutputModelName Value=""/><Assembly Value="0"/><MeshAsSingleBody Value="0"/>
           <Retain2DSurfaceBodies Value="0"/><FillCavity Value="1"/><MixedMesh Value="0"/>
           <PreserveFaceMesh Value="0"/><StraightenEdges Checked="1"/>
           <PreserveSurfaceSkew Checked="0" Value="55"/>
          </AdvancedOptions>
         </TetMesher>''')

    elif mesh_type == "Hex":
        simlab.execute(f''' <AutoHexMesh UUID="f4ce8a5e-4df8-42de-ab98-547a83e9d7c2">
          <InputBodies>
           <Entities>
            <Model>{mesh_model}</Model>
            <Body>"{BODY_NAME}",</Body>
           </Entities>
          </InputBodies>
          <AverageElementSize Value="{vol_mesh_size} mm"/>
          <MinimumElementSize Value="{vol_mesh_size*0.1:.3f} mm"/>
          <AllowQuadMeshTransition Checked="0"/>
          <CreateMeshInNewModel Checked="0"/>
          <CreateRingAlongCircleAndSlot Checked="1"/>
          <AvoidSpiderWedgeAlongAxis Checked="0"/>
         </AutoHexMesh>''')
    print(f"  OK {mesh_type} volume mesh done")

    # ===============================================================
    # PHASE 5: MOVE TO ROOT
    # ===============================================================
    print(f"\n-- PHASE 5: Move to Root -----------------------------------")
    simlab.execute(f'''<MoveSubModelBodiesToRootModel UUID="0619e34b-2275-40b0-b479-882d179d560b">
      <BodiesToMove>
       <Entities>
        <Model>{mesh_model}</Model>
        <Body>"{BODY_NAME}",</Body>
       </Entities>
      </BodiesToMove>
     </MoveSubModelBodiesToRootModel>''')
    print(f"  OK {BODY_NAME} moved to root of {mesh_model}")

    print("\n" + "=" * 60)
    print(f"  {BODY_NAME} complete!")
    print("=" * 60)
