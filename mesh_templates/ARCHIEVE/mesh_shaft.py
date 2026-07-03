# =============================================================================
# SCRIPT  : mesh_shaft.py
# PURPOSE : Complete mesh workflow for SHAFT
# =============================================================================

from hwx import simlab
import os

# ── USER INPUTS ───────────────────────────────────────────────────────────────
mesh_size  = 4
mesh_type  = "Tet4"
AREA_CSV   = "C:/Users/PranavBhojane/Desktop/New_folder/SIMLAB_AUTOMATION/TEMP/shaft_area.csv"
TARGET_AREA = 527.9
TOLERANCE   = 10.0
# ─────────────────────────────────────────────────────────────────────────────

MODEL     = "$Geometry"
BODY_NAME = "SHAFT"

print("=" * 60)
print(f"  SHAFT — Complete Mesh Workflow")
print("=" * 60)

# ═══════════════════════════════════════════════════════════════
# PHASE 1: MESH CONTROLS
# ═══════════════════════════════════════════════════════════════
print("\n── PHASE 1: Mesh Controls ──────────────────────────────────")

def apply_isoline_cyl(body, r_min, r_max, mc_name, axial, circ, color="0,255,0,"):
    simlab.execute(f'''<SelectFeatures UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E" CheckBox="ON">
  <SupportEntities><Entities><Model>{MODEL}</Model><Body>"{body}",</Body></Entities></SupportEntities>
  <Arcs MaxValue="0 mm" MinValue="0 mm" Value="0"/><ArcsAll Value="2"/>
  <Circles MaxValue="0 mm" MinValue="0 mm" Value="0"/><CirclesAll Value="0"/>
  <Cones MaxValue="0 mm" MinValue="0 mm" Value="0"/><ConeAll Value="0"/>
  <FullCone Value="0"/><ClosedPartialCone Value="0"/><OpenPartialCone Value="0"/>
  <TaperAngle Angle="0 deg" Value="0"/>
  <Dics MaxValue="0 mm" MinValue="0 mm" Value="0"/><DicsAll Value="0"/>
  <HollowDics MaxValue="0 mm" MinValue="0 mm" Value="0"/><HollowDicsAll Value="0"/>
  <Cylinders MaxValue="{r_max} mm" MinValue="{r_min} mm" Value="1"/><CylindersAll Value="0"/>
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
  <CreateGrp Value="1" Name="{mc_name}_Faces"/>
 </SelectFeatures>''')
    faces = simlab.getSelectedEntities("Face")
    print(f"  {mc_name}: {len(faces) if faces else 0} faces")
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
   <UseAxialSize Value="1"/><AxialSize Value="{axial} mm"/><AxialNumElems Value="0"/>
   <UseCirAngle Value="0"/><CirAngle Value="0 deg"/><CirNumElems Value="{circ}"/>
   <AspectRatio Value="10"/><MinElemSize Value="0 mm"/><MergeFaces Value="1"/>
   <CreateUniformMesh Value="0"/><StartPointPicked Value="0"/>
   <CentreX Value="0 mm"/><CentreY Value="0 mm"/><CentreZ Value="0 mm"/>
   <RevDirection Value="0"/><ExtendLayers Value="0"/><AlignStartPointToLocalAxis Value="0"/>
  </IsoLine>
 </MeshControl>''')
        print(f"  ✓ {mc_name} applied")

# MC1: Inner Race seating r=7.4-7.6mm, 2.5mm axial, 16 circ
print("\n[MC1] Inner Race seating (r=7.4-7.6mm)...")
apply_isoline_cyl(BODY_NAME, 7.4, 7.6, "SHAFT_IsoLine_InnerRace", 2.5, 16, "0,255,255,")

# MC2: Stator seating r=7.7-7.75mm, 2mm axial, 6 circ
print("\n[MC2] Stator seating (r=7.7-7.75mm)...")
apply_isoline_cyl(BODY_NAME, 7.7, 7.75, "SHAFT_IsoLine_Stator", 2, 6, "0,255,0,")

# ═══════════════════════════════════════════════════════════════
# PHASE 2: SURFACE MESH
# ═══════════════════════════════════════════════════════════════
print("\n── PHASE 2: Surface Mesh ───────────────────────────────────")
simlab.execute(f'''<SurfaceMesh UUID="08df0ff6-f369-4003-956c-82781326c876">
  <tag Value="-1"/>
  <SurfaceMeshType Value="Tri"/>
  <SupportEntities><Entities><Model>{MODEL}</Model><Body>"{BODY_NAME}",</Body></Entities></SupportEntities>
  <Tri>
   <ElementType Value="Tri3"/>
   <AverageElementSize Checked="1" Value="{mesh_size} mm"/>
   <MaximumElementSize Checked="0" Value="{mesh_size*1.414:.3f} mm"/>
   <MinimumElementSize Value="{mesh_size*0.1:.3f} mm"/>
   <GradeFactor Value="1.5"/>
   <MaximumAnglePerElement Value="45 deg"/>
   <CurvatureMinimumElementSize Value="{mesh_size*0.5:.3f} mm"/>
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
print("  ✓ Surface mesh done")

all_models = simlab.getAllRootModelNames("all")
mesh_model = next((m for m in all_models if m != MODEL and
                   ("_SM" in m or m.endswith(".gda"))), None)
print(f"  Mesh model: {mesh_model}")

# ═══════════════════════════════════════════════════════════════
# PHASE 3: CHANGE LAYERS — Stator seating faces
# ═══════════════════════════════════════════════════════════════
print("\n── PHASE 3: Change Layers — Stator seating faces ──────────")

# Step 3a: SelectFeatures on mesh model
print("\n[3a] SelectFeatures stator cyl faces (r=7.7-7.75mm)...")
simlab.execute(f'''<SelectFeatures UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E" CheckBox="ON">
  <SupportEntities><Entities><Model>{mesh_model}</Model><Body>"{BODY_NAME}",</Body></Entities></SupportEntities>
  <Arcs MaxValue="0 mm" Value="0" MinValue="0 mm"/><ArcsAll Value="255"/>
  <Circles MaxValue="0 mm" Value="0" MinValue="0 mm"/><CirclesAll Value="0"/>
  <Cones MaxValue="0 mm" Value="0" MinValue="0 mm"/><ConeAll Value="0"/>
  <FullCone Value="0"/><ClosedPartialCone Value="0"/><OpenPartialCone Value="0"/>
  <TaperAngle Value="0" Angle="0 deg"/>
  <Dics MaxValue="0 mm" Value="0" MinValue="0 mm"/><DicsAll Value="0"/>
  <HollowDics MaxValue="0 mm" Value="0" MinValue="0 mm"/><HollowDicsAll Value="0"/>
  <Cylinders MaxValue="7.75 mm" Value="1" MinValue="7.7 mm"/><CylindersAll Value="0"/>
  <FullCylinder Value="1"/><ClosedPartialCylinder Value="1"/><OpenPartialCylinder Value="1"/>
  <Fillets MaxValue="0 mm" Value="0" MinValue="0 mm"/><FilletsOption Value="1"/>
  <PlanarFaces Value="0"/><FourEdgedFaces Value="0"/><ConnectedCoaxialFaces Value="0"/>
  <ThroughBoltHole MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <BlindBoltHole MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <BlindBoltHoleDepth MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <SlotEdges MaxValue="0 mm" Value="0" MinValue="0 mm"/><SlotEdgesAll Value="0"/>
  <ArcLengthBased Value=""/><AngleBased Value=""/>
  <SharpEdges Value="" Option="" Angle=""/><ThicknessBased Value=""/>
  <LogosAndDetails Value=""/><LogosAndDetailsThickness Value=""/>
  <CreateGrp Value="1" Name="SHAFT_Stator_Cyl_Faces"/>
 </SelectFeatures>''')

stator_cyl_faces = simlab.getSelectedEntities("Face")
print(f"  Stator cyl faces: {len(stator_cyl_faces) if stator_cyl_faces else 0}")

if not stator_cyl_faces:
    print("  ✗ No stator seating faces — skipping ChangeLayers")
else:
    # Step 3b: SelectAdjacent
    print("\n[3b] SelectAdjacent...")
    face_str_cyl = ",".join(str(f) for f in stator_cyl_faces) + ","
    simlab.execute(f'''<SelectAdjacent UUID="06104eca-3dbf-45af-a99c-953c8fe0f4e4" recordable="0">
  <tag Value="-1"/><Name Value=""/>
  <SupportEntities><Entities><Model>{mesh_model}</Model><Face>{face_str_cyl}</Face></Entities></SupportEntities>
  <NoofLayer Value="-1"/><VisiblesFaceOnly Value="0"/>
  <SelectAdjacent Value="1"/><IgnoreSharedFaces Value="0"/>
 </SelectAdjacent>''')
    all_selected_faces = simlab.getSelectedEntities("Face")
    print(f"  Adjacent faces: {len(all_selected_faces) if all_selected_faces else 0}")

    # Step 3c: MergeFaces
    print("\n[3c] MergeFaces...")
    all_face_str = ",".join(str(f) for f in all_selected_faces) + ","
    simlab.execute(f'''<MergeFace UUID="D9D604CE-B512-44e3-984D-DF3E64141F8D">
  <Name Value="SHAFT_MergeFace_Stator"/>
  <SupportEntities><Entities><Model>{mesh_model}</Model><Face>{all_face_str}</Face></Entities></SupportEntities>
  <MergeBoundaryEdges Value="1"/><SplitBoundaryEdges Value="0"/>
  <SplitEdgesBasedon Value="0"/><FeatureAngle Value="45 deg"/>
  <RedoFlag Value=""/><tag Value="-1"/>
 </MergeFace>''')
    print("  ✓ Faces merged")

    # Step 3d: Find merged face by area
    print("\n[3d] Finding merged face by area...")
    simlab.showOrHideEntities([BODY_NAME], "IsolateShow", mesh_model)
    simlab.createGroupFromVisibleEntities("Face", "SHAFT_VISIBLE_FACES")
    all_mesh_faces = simlab.getEntityFromGroup("SHAFT_VISIBLE_FACES")
    print(f"  Total mesh faces: {len(all_mesh_faces)}")

    face_str_all = ",".join(str(f) for f in all_mesh_faces) + ","
    if os.path.exists(AREA_CSV):
        os.remove(AREA_CSV)
    simlab.execute(f'''<CalculateArea UUID="e77c854e-2658-4034-a3a4-1b46b72e4770">
  <InputEntities><Entities><Model>{mesh_model}</Model><Face>{face_str_all}</Face></Entities></InputEntities>
  <FileName Value="{AREA_CSV}"/>
 </CalculateArea>''')

    surviving_face = None
    with open(AREA_CSV, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("Face"):
                parts = line.split(",")
                fid  = int(parts[0].replace("Face", "").strip())
                area = float(parts[1].replace("mm2", "").strip())
                if abs(area - TARGET_AREA) <= TOLERANCE:
                    surviving_face = fid
                    print(f"  Merged face: {fid} (area={area:.2f} mm²)")
                    break

    if not surviving_face:
        print("  ✗ Merged face not found")
    else:
        # Step 3e: SplitFace
        print(f"\n[3e] SplitFace on face {surviving_face}...")
        simlab.execute(f'''<FEASplitFace UUID="F67108F4-D1EB-4fc9-9333-8B181405C673">
  <tag Value="-1"/>
  <Name Value="SHAFT_SplitFace_Stator"/>
  <SupportEntities><Entities><Model>{mesh_model}</Model><Face>{surviving_face},</Face></Entities></SupportEntities>
  <FeatureAngle Value="15 deg"/><Option Value="0"/><CreateFloatingEdges Value="1"/>
 </FEASplitFace>''')
        print("  ✓ Face split by 15 deg")

        # Step 3f: Reselect after split and ChangeLayers
        print("\n[3f] Reselect and ChangeLayers...")
        simlab.execute(f'''<SelectFeatures UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E" CheckBox="ON">
  <SupportEntities><Entities><Model>{mesh_model}</Model><Body>"{BODY_NAME}",</Body></Entities></SupportEntities>
  <Arcs MaxValue="0 mm" Value="0" MinValue="0 mm"/><ArcsAll Value="255"/>
  <Circles MaxValue="0 mm" Value="0" MinValue="0 mm"/><CirclesAll Value="0"/>
  <Cones MaxValue="0 mm" Value="0" MinValue="0 mm"/><ConeAll Value="0"/>
  <FullCone Value="0"/><ClosedPartialCone Value="0"/><OpenPartialCone Value="0"/>
  <TaperAngle Value="0" Angle="0 deg"/>
  <Dics MaxValue="0 mm" Value="0" MinValue="0 mm"/><DicsAll Value="0"/>
  <HollowDics MaxValue="0 mm" Value="0" MinValue="0 mm"/><HollowDicsAll Value="0"/>
  <Cylinders MaxValue="7.75 mm" Value="1" MinValue="7.7 mm"/><CylindersAll Value="0"/>
  <FullCylinder Value="1"/><ClosedPartialCylinder Value="1"/><OpenPartialCylinder Value="1"/>
  <Fillets MaxValue="0 mm" Value="0" MinValue="0 mm"/><FilletsOption Value="1"/>
  <PlanarFaces Value="0"/><FourEdgedFaces Value="0"/><ConnectedCoaxialFaces Value="0"/>
  <ThroughBoltHole MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <BlindBoltHole MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <BlindBoltHoleDepth MaxValue="0 mm" Value="0" MinValue="0 mm"/>
  <SlotEdges MaxValue="0 mm" Value="0" MinValue="0 mm"/><SlotEdgesAll Value="0"/>
  <ArcLengthBased Value=""/><AngleBased Value=""/>
  <SharpEdges Value="" Option="" Angle=""/><ThicknessBased Value=""/>
  <LogosAndDetails Value=""/><LogosAndDetailsThickness Value=""/>
  <CreateGrp Value="1" Name="SHAFT_Stator_Final"/>
 </SelectFeatures>''')

        final_faces = simlab.getSelectedEntities("Face")
        print(f"  Faces after split: {len(final_faces) if final_faces else 0}")

        if final_faces:
            final_face_str = ",".join(str(f) for f in final_faces) + ","
            simlab.execute(f'''<ChangeLayers UUID="0480248b-fbe6-4da3-ba06-74147e68e9c0">
  <tag Value="-1"/>
  <Name Value="SHAFT_ChangeLayers_Stator"/>
  <InputType Value="Faces"/>
  <Faces>
   <Faces><Entities><Model>{mesh_model}</Model><Face>{final_face_str}</Face></Entities></Faces>
   <Axial Value="1"/>
   <AxialNumElements Value="5" Checked="1"/>
   <AxialElemSize Value="2.5 mm" Checked="0"/>
   <Range Value="0"/><StartNode/><EndNode/>
   <Circular Value="1"/>
   <CircularNumElements Value="24" Checked="1"/>
   <CircularElemSize Value="5 deg" Checked="0"/>
   <PrincipalDirection Value="1"/>
  </Faces>
  <EdgesOrElemEdges>
   <EdgesOrElemEdges Value=""/>
   <NumberOfLayers Value="5" Checked=""/>
   <MeshSize Value="5" Checked="0"/>
   <Node Value=""/>
  </EdgesOrElemEdges>
  <Output/>
 </ChangeLayers>''')
            print("  ✓ ChangeLayers applied")

# ═══════════════════════════════════════════════════════════════
# PHASE 4: QUALITY CHECK + CLEANUP
# ═══════════════════════════════════════════════════════════════
print("\n── PHASE 4: Quality Check + Cleanup ────────────────────────")
for opt, cond, name, extra in [
    ("Compute", "G Than Or Eq", "Aspect Ratio", 'LimitValue="10"'),
    ("Cleanup", "L Than and G Than Or Eq", "Edge Length",
     'MaximumLimitValue="100 mm" MinimumLimitValue="0.25 mm"'),
    ("Cleanup", "L Than", "Height", 'LimitValue="0.2 mm"'),
]:
    simlab.execute(f'''<QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
  <ElementType Value="Tri"/><Option Value="{opt}"/>
  <Quality Condition="{cond}" {extra} Name="{name}"/>
  <SupportEntities><Entities><Model>{mesh_model}</Model><Body>"{BODY_NAME}",</Body></Entities></SupportEntities>
  <CleanupType Value="Modify Element"/><PreserveSurfaceSkew Check="0" Value="55"/>
 </QCheck>''')
print("  ✓ Quality cleanup done")

# ═══════════════════════════════════════════════════════════════
# PHASE 5: VOLUME MESH
# ═══════════════════════════════════════════════════════════════
print(f"\n── PHASE 5: Volume Mesh ({mesh_type}) ──────────────────────")
tet_type = "Tet4" if mesh_type == "Tet4" else "Tet10StraightEdge"
simlab.execute(f'''<TetMesher UUID="83822e68-12bb-43b9-b2ac-77e0b9ea5149">
  <tag Value="-1"/>
  <Name Value="{BODY_NAME}_TetMesh_{mesh_type}"/>
  <SupportEntities><Entities><Model>{mesh_model}</Model><Body>"{BODY_NAME}",</Body></Entities></SupportEntities>
  <MeshType Value="{tet_type}"/>
  <AverageElemSize Value="{mesh_size} mm"/>
  <MaxElemSize Checked="0" Value="0"/><InternalGrading Value="2"/>
  <MinQuality Value="0.12"/><LinearQuality Value="2"/><MaxQuality Value="1"/>
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
print(f"  ✓ {mesh_type} volume mesh done")

# ═══════════════════════════════════════════════════════════════
# PHASE 6: MOVE TO ROOT
# ═══════════════════════════════════════════════════════════════
print(f"\n── PHASE 6: Move to Root ───────────────────────────────────")
simlab.execute(f'''<MoveSubModelBodiesToRootModel UUID="0619e34b-2275-40b0-b479-882d179d560b">
  <BodiesToMove><Entities><Model>{mesh_model}</Model><Body>"{BODY_NAME}",</Body></Entities></BodiesToMove>
 </MoveSubModelBodiesToRootModel>''')
print(f"  ✓ {BODY_NAME} moved to root of {mesh_model}")

print("\n" + "=" * 60)
print(f"  SHAFT complete!")
print("=" * 60)
