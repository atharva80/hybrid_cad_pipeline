# -*- coding: utf-8 -*-
# =============================================================================
# SCRIPT  : mesh_races.py
# PURPOSE : Mesh controls + Surface + Quality + Volume + Move to root for:
#           OUTER_RACE / OUTER_RACE_1 → merge → OUTER_RACE
#           MID_RACE x4              → merge → MID_RACE
#           INNER_RACE / INNER_RACE_1 → merge → INNER_RACE
# =============================================================================

from hwx import simlab

# -- USER INPUTS ---------------------------------------------------------------
# -----------------------------------------------------------------------------

MODEL = "$Geometry"


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
    
    import os
    import time
    log_file = os.path.join(os.path.dirname(__file__), "..", "_cache", "meshing_debug.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    def truth_log(msg, force_print=True):
        if force_print:
            print(msg)
        try:
            with open(log_file, "a") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] [{BODY_NAME}] {msg}\n")
        except:
            pass

    truth_log("=" * 60)
    truth_log(f"Mesh Workflow - OUTER_RACE, MID_RACE, INNER_RACE")
    truth_log(f"Mesh Size: {mesh_size}mm | Type: {mesh_type}")
    truth_log("=" * 60)

    def apply_isoline(body_name, r_min, r_max, mc_name, axial_size, cir_elems, color="0,255,0,"):
        grp = f"{mc_name}_Faces"
        simlab.execute(f'''<SelectFeatures UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E" CheckBox="ON">
      <SupportEntities><Entities><Model>{MODEL}</Model><Body>"{body_name}",</Body></Entities></SupportEntities>
      <Arcs MaxValue="0 mm" MinValue="0 mm" Value="0"/><ArcsAll Value="2"/>
      <Circles MaxValue="0 mm" MinValue="0 mm" Value="0"/><CirclesAll Value="0"/>
      <Cones MaxValue="0 mm" MinValue="0 mm" Value="0"/><ConeAll Value="0"/>
      <FullCone Value="0"/><ClosedPartialCone Value="0"/><OpenPartialCone Value="0"/>
      <TaperAngle Angle="0 deg" Value="0"/>
      <Dics MaxValue="0 mm" MinValue="0 mm" Value="0"/><DicsAll Value="0"/>
      <HollowDics MaxValue="0 mm" MinValue="0 mm" Value="0"/><HollowDicsAll Value="0"/>
      <Cylinders MaxValue="{r_max} mm" MinValue="{r_min} mm" Value="1"/><CylindersAll Value="0"/>
      <FullCylinder Value="1"/><ClosedPartialCylinder Value="0"/><OpenPartialCylinder Value="0"/>
      <Fillets MaxValue="3 mm" MinValue="0.51 mm" Value="0"/><FilletsOption Value="1"/>
      <PlanarFaces Value="0"/><FourEdgedFaces Value="0"/><ConnectedCoaxialFaces Value="0"/>
      <ThroughBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
      <BlindBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
      <BlindBoltHoleDepth MaxValue="0 mm" MinValue="0 mm" Value="0"/>
      <SlotEdges MaxValue="0 mm" MinValue="0 mm" Value="0"/><SlotEdgesAll Value="0"/>
      <ArcLengthBased Value=""/><AngleBased Value=""/>
      <SharpEdges Option="" Angle="" Value=""/><ThicknessBased Value=""/>
      <LogosAndDetails Value=""/><LogosAndDetailsThickness Value=""/>
      <CreateGrp Value="1" Name="{grp}"/>
     </SelectFeatures>''')
        faces = simlab.getSelectedEntities("Face")
        print(f"    {mc_name}: {len(faces) if faces else 0} faces (r={r_min}-{r_max}mm)")
        if faces:
            face_str = ",".join(str(f) for f in faces) + ","
            simlab.execute(f'''<MeshControl UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" isObject="1" CheckBox="ON">
      <tag Value="-1"/>
      <MeshControlName Value="{mc_name}"/>
      <MeshControlType Value="IsoLine"/>
      <Entities><Entities><Model>{MODEL}</Model><Face>{face_str}</Face></Entities></Entities>
      <Reverse ModelIds="" Value="" EntityTypes=""/>
      <MeshColor Value="{color}"/>
      <IsoLine>
       <UseAxialSize Value="1"/><AxialSize Value="{axial_size} mm"/><AxialNumElems Value="0"/>
       <UseCirAngle Value="0"/><CirAngle Value="0 deg"/><CirNumElems Value="{cir_elems}"/>
       <AspectRatio Value="10"/><MinElemSize Value="0 mm"/><MergeFaces Value="1"/>
       <CreateUniformMesh Value="0"/><StartPointPicked Value="0"/>
       <CentreX Value="0 mm"/><CentreY Value="0 mm"/><CentreZ Value="0 mm"/>
       <RevDirection Value="0"/><ExtendLayers Value="0"/><AlignStartPointToLocalAxis Value="0"/>
      </IsoLine>
     </MeshControl>''')
            print(f"    OK {mc_name} applied")

    def surface_mesh_bodies(body_str, size):
        simlab.execute(f'''<SurfaceMesh UUID="08df0ff6-f369-4003-956c-82781326c876">
      <tag Value="-1"/>
      <SurfaceMeshType Value="Tri"/>
      <SupportEntities><Entities><Model>{MODEL}</Model><Body>{body_str}</Body></Entities></SupportEntities>
      <Tri>
       <ElementType Value="Tri3"/>
       <AverageElementSize Checked="1" Value="{size} mm"/>
       <MaximumElementSize Checked="0" Value="{size*1.414:.3f} mm"/>
       <MinimumElementSize Value="{size*0.1:.3f} mm"/>
       <GradeFactor Value="1.5"/>
       <MaximumAnglePerElement Value="45 deg"/>
       <CurvatureMinimumElementSize Value="{size*0.5:.3f} mm"/>
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

    def quality_cleanup(mesh_model, body_str):
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
      <SupportEntities><Entities><Model>{mesh_model}</Model><Body>{body_str}</Body></Entities></SupportEntities>
      <CleanupType Value="Modify Element"/><PreserveSurfaceSkew Check="0" Value="55"/>
     </QCheck>''')

    def volume_mesh(mesh_model, body_str, label, size, mtype):
        if mesh_type in ("Tet4", "Tet10"):
            tet_type = "Tet4" if mtype == "Tet4" else "Tet10StraightEdge"
            simlab.execute(f'''<TetMesher UUID="83822e68-12bb-43b9-b2ac-77e0b9ea5149">
              <tag Value="-1"/>
              <Name Value="{label}_TetMesh_{mtype}"/>
              <SupportEntities><Entities><Model>{mesh_model}</Model><Body>{body_str}</Body></Entities></SupportEntities>
              <MeshType Value="{tet_type}"/>
              <AverageElemSize Value="{size} mm"/>
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
                <Body>{body_str}</Body>
               </Entities>
              </InputBodies>
              <AverageElementSize Value="{size} mm"/>
              <MinimumElementSize Value="{size*0.1:.3f} mm"/>
              <AllowQuadMeshTransition Checked="0"/>
              <CreateMeshInNewModel Checked="0"/>
              <CreateRingAlongCircleAndSlot Checked="1"/>
              <AvoidSpiderWedgeAlongAxis Checked="0"/>
             </AutoHexMesh>''')

    def merge_bodies(body_names, output_name, model):
        body_str = "".join(f'"{b}",' for b in body_names)
        simlab.execute(f'''<BodyMerge gda="" UUID="FA9128EE-5E6C-49af-BADF-4016E5622020">
      <tag Value="-1"/><Name Value=""/>
      <SupportEntities><Entities><Model>{model}</Model><Body>{body_str}</Body></Entities></SupportEntities>
      <Delete_Shared_Faces Value="0"/>
      <Output_Body_Name Value="{output_name}"/>
      <RedoFlag Value=""/><Output/>
     </BodyMerge>''')
        print(f"  OK Merged -> '{output_name}'")

    def rename_body(model, old_name, new_name):
        simlab.execute(f'''<RenameBody UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
      <SupportEntities>
       <Entities>
        <Model>{model}</Model>
        <Body>"{old_name}",</Body>
       </Entities>
      </SupportEntities>
      <NewName Value="{new_name}"/>
      <Output/>
     </RenameBody>''')
        print(f"  OK Renamed '{old_name}' -> '{new_name}'")

    def move_to_root(mesh_model, body_name):
        simlab.execute(f'''<MoveSubModelBodiesToRootModel UUID="0619e34b-2275-40b0-b479-882d179d560b">
      <BodiesToMove>
       <Entities>
        <Model>{mesh_model}</Model>
        <Body>"{body_name}",</Body>
       </Entities>
      </BodiesToMove>
     </MoveSubModelBodiesToRootModel>''')
        print(f"  OK '{body_name}' moved to root of {mesh_model}")

    def get_mesh_model():
        all_models = simlab.getAllRootModelNames("all")
        return next((m for m in all_models if m != MODEL and
                     ("_SM" in m or m.endswith(".gda"))), MODEL)

    def get_bodies_from_mesh(mesh_model, exact_name):
        """Get body exactly matching exact_name from MESH model."""
        try:
            # Pass empty string to get ALL bodies in the model, then filter in python
            # This guarantees SimLab won't throw a 'Not Found' UI error dialog because the model is never empty
            res = simlab.getBodiesWithSubString(mesh_model, [""])
            return [b for b in res if b == exact_name] if res else []
        except:
            return []

    # ===============================================================
    # IDENTIFY TARGET BODIES
    # ===============================================================
    truth_log(f"Starting target body identification for {BODY_NAME}")
    if BODY_NAME.startswith("BEARING_"):
        # User defined fixed mapping: 1=Outer, 2=Inner, 3 & 4 = Mid Races
        outer_bodies = [f"{BODY_NAME}_1"]
        inner_bodies = [f"{BODY_NAME}_2"]
        mid_bodies   = [f"{BODY_NAME}_3", f"{BODY_NAME}_4"]
        truth_log(f"Strict mapping applied -> OUTER: {outer_bodies} | INNER: {inner_bodies} | MID: {mid_bodies}")
    else:
        # Fallback for old standalone mappings
        outer_bodies = ["OUTER_RACE", "OUTER_RACE_1"]
        inner_bodies = ["INNER_RACE", "INNER_RACE_1"]
        mid_bodies = ["MID_RACE", "MID_RACE_1", "MID_RACE_2", "MID_RACE_3"]

    # ===============================================================
    # OUTER_RACE
    # ===============================================================
    print("\n" + "="*60)
    print("  OUTER_RACE")
    print("="*60)

    if outer_bodies:
        for body in outer_bodies:
            print(f"\n  -- Mesh Controls: {body} --")
            apply_isoline(body, 13.5, 13.6, f"{body}_IsoLine_Inner", 2,   24, "0,255,255,")
            apply_isoline(body, 17.4, 17.6, f"{body}_IsoLine_Outer", 2.5, 28, "0,255,0,")

        print("\n  -- Surface Mesh --")
        outer_str = "".join(f'"{b}",' for b in outer_bodies)
        surface_mesh_bodies(outer_str, mesh_size)
        print("  OK Surface mesh done")

        mesh_model = get_mesh_model()
        print(f"  Mesh model: {mesh_model}")

        print("\n  -- Quality Cleanup --")
        quality_cleanup(mesh_model, outer_str)
        print("  OK Quality cleanup done")

        print(f"\n  -- Volume Mesh ({mesh_type}) --")
        # For volume meshing, only grab bodies that actually got surface meshed
        # We can rely on prefix search for OUTER_RACE if it was renamed, but since it's dynamic we use original names
        outer_vm = []
        for ob in outer_bodies:
            outer_vm.extend(get_bodies_from_mesh(mesh_model, ob))
        
        outer_vm_str = "".join(f'"{b}",' for b in outer_vm)
        if outer_vm:
            print(f"  Volume mesh bodies: {outer_vm}")
            volume_mesh(mesh_model, outer_vm_str, f"{BODY_NAME}_OUTER", mesh_size, mesh_type)
            print("  OK Volume mesh done")

            print("\n  -- Merge/Rename -> OUTER_RACE --")
            if len(outer_vm) >= 2:
                merge_bodies(outer_vm, f"{BODY_NAME}_OUTER", mesh_model)
            elif len(outer_vm) == 1:
                rename_body(mesh_model, outer_vm[0], f"{BODY_NAME}_OUTER")
            
            print("\n  -- Move to Root --")
            move_to_root(mesh_model, f"{BODY_NAME}_OUTER")
            
            # Verify if it actually worked!
            if get_bodies_from_mesh(MODEL, f"{BODY_NAME}_OUTER"):
                truth_log(f"SUCCESS: Volume mesh '{BODY_NAME}_OUTER' verified in Root!")
            else:
                truth_log(f"ERROR: Volume mesh '{BODY_NAME}_OUTER' SILENTLY FAILED! Not found in Root!")
        else:
            truth_log(f"WARNING: Surface mesh for OUTER_RACE produced zero bodies, skipping Volume mesh.")
    else:
        truth_log("No OUTER_RACE bodies found in CAD to mesh.")

    # ===============================================================
    # MID_RACE
    # ===============================================================
    print("\n" + "="*60)
    print("  MID_RACE")
    print("="*60)

    if mid_bodies:
        for body in mid_bodies:
            print(f"\n  -- Mesh Controls: {body} --")
            apply_isoline(body, 11.4, 11.5, f"{body}_IsoLine_Inner", 2, 20, "0,255,255,")
            apply_isoline(body, 13.5, 13.6, f"{body}_IsoLine_Outer", 2, 20, "0,255,0,")

        print("\n  -- Surface Mesh --")
        mid_str = "".join(f'"{b}",' for b in mid_bodies)
        surface_mesh_bodies(mid_str, mesh_size)
        print("  OK Surface mesh done")

        mesh_model = get_mesh_model()
        print(f"  Mesh model: {mesh_model}")

        print("\n  -- Quality Cleanup --")
        quality_cleanup(mesh_model, mid_str)
        print("  OK Quality cleanup done")

        print(f"\n  -- Volume Mesh ({mesh_type}) --")
        mid_vm = []
        for mb in mid_bodies:
            mid_vm.extend(get_bodies_from_mesh(mesh_model, mb))

        mid_vm_str = "".join(f'"{b}",' for b in mid_vm)
        if mid_vm:
            print(f"  Volume mesh bodies: {mid_vm}")
            volume_mesh(mesh_model, mid_vm_str, f"{BODY_NAME}_MID", mesh_size, mesh_type)
            print("  OK Volume mesh done")

            print("\n  -- Merge/Rename -> MID_RACE --")
            if len(mid_vm) >= 2:
                merge_bodies(mid_vm, f"{BODY_NAME}_MID", mesh_model)
            elif len(mid_vm) == 1:
                rename_body(mesh_model, mid_vm[0], f"{BODY_NAME}_MID")

            print("\n  -- Move to Root --")
            move_to_root(mesh_model, f"{BODY_NAME}_MID")
            
            # Verify if it actually worked!
            if get_bodies_from_mesh(MODEL, f"{BODY_NAME}_MID"):
                truth_log(f"SUCCESS: Volume mesh '{BODY_NAME}_MID' verified in Root!")
            else:
                truth_log(f"ERROR: Volume mesh '{BODY_NAME}_MID' SILENTLY FAILED! Not found in Root!")
        else:
            truth_log(f"WARNING: Surface mesh for MID_RACE produced zero bodies, skipping Volume mesh.")
    else:
        truth_log("No MID_RACE bodies found in CAD to mesh.")

    # ===============================================================
    # INNER_RACE
    # ===============================================================
    print("\n" + "="*60)
    print("  INNER_RACE")
    print("="*60)

    if inner_bodies:
        for body in inner_bodies:
            print(f"\n  -- Mesh Controls: {body} --")
            apply_isoline(body, 7.4,  7.6,  f"{body}_IsoLine_Inner", 2.5, 16, "0,255,255,")
            apply_isoline(body, 11.4, 11.5, f"{body}_IsoLine_Outer", 2,   20, "0,255,0,")

        print("\n  -- Surface Mesh --")
        inner_str = "".join(f'"{b}",' for b in inner_bodies)
        surface_mesh_bodies(inner_str, mesh_size)
        print("  OK Surface mesh done")

        mesh_model = get_mesh_model()
        print(f"  Mesh model: {mesh_model}")

        print("\n  -- Quality Cleanup --")
        quality_cleanup(mesh_model, inner_str)
        print("  OK Quality cleanup done")

        print(f"\n  -- Volume Mesh ({mesh_type}) --")
        inner_vm = []
        for ib in inner_bodies:
            inner_vm.extend(get_bodies_from_mesh(mesh_model, ib))

        inner_vm_str = "".join(f'"{b}",' for b in inner_vm)
        if inner_vm:
            print(f"  Volume mesh bodies: {inner_vm}")
            volume_mesh(mesh_model, inner_vm_str, f"{BODY_NAME}_INNER", mesh_size, mesh_type)
            print("  OK Volume mesh done")

            print("\n  -- Merge/Rename -> INNER_RACE --")
            if len(inner_vm) >= 2:
                merge_bodies(inner_vm, f"{BODY_NAME}_INNER", mesh_model)
            elif len(inner_vm) == 1:
                rename_body(mesh_model, inner_vm[0], f"{BODY_NAME}_INNER")

            print("\n  -- Move to Root --")
            move_to_root(mesh_model, f"{BODY_NAME}_INNER")
            
            # Verify if it actually worked!
            if get_bodies_from_mesh(MODEL, f"{BODY_NAME}_INNER"):
                truth_log(f"SUCCESS: Volume mesh '{BODY_NAME}_INNER' verified in Root!")
            else:
                truth_log(f"ERROR: Volume mesh '{BODY_NAME}_INNER' SILENTLY FAILED! Not found in Root!")
        else:
            truth_log(f"WARNING: Surface mesh for INNER_RACE produced zero bodies, skipping Volume mesh.")
    else:
        truth_log("No INNER_RACE bodies found in CAD to mesh.")

    truth_log("=" * 60)
    truth_log("All done - OUTER_RACE, MID_RACE, INNER_RACE meshed")
    print("=" * 60)
