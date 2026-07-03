# -*- coding: utf-8 -*-
# =============================================================================
# SCRIPT  : mesh_display_pcb.py
# PURPOSE : Complete mesh workflow for DISPLAY_PCB
#           1. Remove holes r=0-2mm
#           2. IsoLine MC — Cyl faces r=2.05-2.15mm, 2mm axial, 8 circ
#           3. Surface mesh 3.5mm
#           4. Quality check + cleanup
#           5. Volume mesh 3.5mm
#           6. Move to root
# =============================================================================

from hwx import simlab

# -- USER INPUTS ---------------------------------------------------------------
# -----------------------------------------------------------------------------



def run(BODY_NAME, config):
    def _v(key, default=None):
        val = config.get(key)
        return val if val is not None else default

    MODEL = "$Geometry"
    mesh_size = _v('global.mesh_size', 4.0)
    surf_mesh_size = _v('global.surf_mesh_size', 4.0)
    vol_mesh_size = _v('global.vol_mesh_size', 4.0)
    mesh_type = _v('global.mesh_type', 'Tet4')

    temp_dir = config.get('__temp_dir__', 'C:/temp')
    TARGET_AREA = _v('special.target_area', 527.9)
    TOLERANCE = _v('special.area_tolerance', 10.0)

    print("=" * 60)
    print(f"  DISPLAY_PCB — Complete Mesh Workflow")
    print(f"  Surface: {surf_mesh_size}mm | Volume: {vol_mesh_size}mm | Type: {mesh_type}")
    print("=" * 60)

    # ===============================================================
    # PHASE 1: REMOVE HOLES (r=0-2mm)
    # ===============================================================
    print("\n-- PHASE 1: Remove Holes (r=0-2mm) ------------------------")
    simlab.execute(f'''<ConnectHole UUID="8393e3d3-a92c-4a40-8cc0-803b4cf2169e">
      <RibOptionType Value="1"/>
      <Entity>
       <Entities>
        <Model>{MODEL}</Model>
        <Body>"{BODY_NAME}",</Body>
       </Entities>
      </Entity>
      <AllRadius Value="0"/>
      <MinRadius Value="0 mm"/>
      <MaxRadius Value="2 mm"/>
      <LocalReMesh Value="0"/>
      <ExcludeHoles/>
      <RedoFlag Value=""/>
     </ConnectHole>''')
    print("  OK Holes removed (r=0-2mm)")

    # ===============================================================
    # PHASE 2: MESH CONTROL — Cyl faces r=2.05-2.15mm
    # ===============================================================
    print("\n-- PHASE 2: Mesh Control -----------------------------------")
    print("\n[MC1] Cyl faces r=2.05-2.15mm...")
    simlab.execute(f'''<SelectFeatures UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E" CheckBox="ON">
      <SupportEntities><Entities><Model>{MODEL}</Model><Body>"{BODY_NAME}",</Body></Entities></SupportEntities>
      <Arcs MaxValue="0 mm" MinValue="0 mm" Value="0"/><ArcsAll Value="2"/>
      <Circles MaxValue="0 mm" MinValue="0 mm" Value="0"/><CirclesAll Value="0"/>
      <Cones MaxValue="0 mm" MinValue="0 mm" Value="0"/><ConeAll Value="0"/>
      <FullCone Value="0"/><ClosedPartialCone Value="0"/><OpenPartialCone Value="0"/>
      <TaperAngle Angle="0 deg" Value="0"/>
      <Dics MaxValue="0 mm" MinValue="0 mm" Value="0"/><DicsAll Value="0"/>
      <HollowDics MaxValue="0 mm" MinValue="0 mm" Value="0"/><HollowDicsAll Value="0"/>
      <Cylinders MaxValue="2.15 mm" MinValue="2.05 mm" Value="1"/><CylindersAll Value="0"/>
      <FullCylinder Value="1"/><ClosedPartialCylinder Value="1"/><OpenPartialCylinder Value="1"/>
      <Fillets MaxValue="3 mm" MinValue="0.51 mm" Value="0"/><FilletsOption Value="1"/>
      <PlanarFaces Value="0"/><FourEdgedFaces Value="0"/><ConnectedCoaxialFaces Value="0"/>
      <ThroughBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
      <BlindBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
      <BlindBoltHoleDepth MaxValue="0 mm" MinValue="0 mm" Value="0"/>
      <SlotEdges MaxValue="0 mm" MinValue="0 mm" Value="0"/><SlotEdgesAll Value="0"/>
      <ArcLengthBased Value=""/><AngleBased Value=""/>
      <SharpEdges Option="" Angle="" Value=""/><ThicknessBased Value=""/>
      <LogosAndDetails Value=""/><LogosAndDetailsThickness Value=""/>
      <CreateGrp Value="1" Name="DISPLAY_PCB_Cyl_Faces"/>
     </SelectFeatures>''')

    faces = simlab.getSelectedEntities("Face")
    print(f"  Faces found: {len(faces) if faces else 0}")

    if faces:
        face_str = ",".join(str(f) for f in faces) + ","
        simlab.execute(f'''<MeshControl UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" isObject="1" CheckBox="ON">
      <tag Value="-1"/>
      <MeshControlName Value="DISPLAY_PCB_IsoLine_Cyl"/>
      <MeshControlType Value="IsoLine"/>
      <Entities><Entities><Model>{MODEL}</Model><Face>{face_str}</Face></Entities></Entities>
      <Reverse ModelIds="" Value="" EntityTypes=""/>
      <MeshColor Value="0,255,0,"/>
      <IsoLine>
       <UseAxialSize Value="1"/><AxialSize Value="2 mm"/><AxialNumElems Value="0"/>
       <UseCirAngle Value="0"/><CirAngle Value="0 deg"/><CirNumElems Value="8"/>
       <AspectRatio Value="10"/><MinElemSize Value="0 mm"/><MergeFaces Value="1"/>
       <CreateUniformMesh Value="0"/><StartPointPicked Value="0"/>
       <CentreX Value="0 mm"/><CentreY Value="0 mm"/><CentreZ Value="0 mm"/>
       <RevDirection Value="0"/><ExtendLayers Value="0"/><AlignStartPointToLocalAxis Value="0"/>
      </IsoLine>
     </MeshControl>''')
        print("  OK IsoLine MC applied")
    else:
        print("  - No cyl faces found")

    # ===============================================================
    # PHASE 3: SURFACE MESH
    # ===============================================================
    print("\n-- PHASE 3: Surface Mesh -----------------------------------")
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
                       ("_SM" in m or m.endswith(".gda"))), None)
    print(f"  Mesh model: {mesh_model}")

    # ===============================================================
    # PHASE 4: QUALITY CHECK + CLEANUP
    # ===============================================================
    print("\n-- PHASE 4: Quality Check + Cleanup ------------------------")
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
    # PHASE 5: VOLUME MESH
    # ===============================================================
    print(f"\n-- PHASE 5: Volume Mesh ({mesh_type}) ----------------------")
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
    print(f"  OK {mesh_type} volume mesh done")

    # ===============================================================
    # PHASE 6: MOVE TO ROOT
    # ===============================================================
    print(f"\n-- PHASE 6: Move to Root -----------------------------------")
    simlab.execute(f'''<MoveSubModelBodiesToRootModel UUID="0619e34b-2275-40b0-b479-882d179d560b">
      <BodiesToMove><Entities><Model>{mesh_model}</Model><Body>"{BODY_NAME}",</Body></Entities></BodiesToMove>
     </MoveSubModelBodiesToRootModel>''')
    print(f"  OK {BODY_NAME} moved to root of {mesh_model}")

    print("\n" + "=" * 60)
    print(f"  DISPLAY_PCB complete!")
    print("=" * 60)
