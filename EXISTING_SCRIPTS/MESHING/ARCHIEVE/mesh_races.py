# =============================================================================
# SCRIPT  : mesh_races.py
# PURPOSE : Mesh controls + Surface + Quality + Volume + Move to root for:
#           OUTER_RACE / OUTER_RACE_1 → merge → OUTER_RACE
#           MID_RACE x4              → merge → MID_RACE
#           INNER_RACE / INNER_RACE_1 → merge → INNER_RACE
# =============================================================================

from hwx import simlab

# ── USER INPUTS ───────────────────────────────────────────────────────────────
mesh_size = 4      # Average element size mm
mesh_type = "Tet4" # "Tet4" or "Tet10"
# ─────────────────────────────────────────────────────────────────────────────

MODEL = "$Geometry"

print("=" * 60)
print("  Mesh Workflow — OUTER_RACE, MID_RACE, INNER_RACE")
print(f"  Mesh Size: {mesh_size}mm | Type: {mesh_type}")
print("=" * 60)

# ── Helper: IsoLine Mesh Control ─────────────────────────────────────────────
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
        print(f"    ✓ {mc_name} applied")

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
    for opt, cond, name, extra in [
        ("Compute", "G Than Or Eq", "Aspect Ratio", 'LimitValue="10"'),
        ("Cleanup", "L Than and G Than Or Eq", "Edge Length",
         'MaximumLimitValue="100 mm" MinimumLimitValue="0.25 mm"'),
        ("Cleanup", "L Than", "Height", 'LimitValue="0.2 mm"'),
    ]:
        simlab.execute(f'''<QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
  <ElementType Value="Tri"/><Option Value="{opt}"/>
  <Quality Condition="{cond}" {extra} Name="{name}"/>
  <SupportEntities><Entities><Model>{mesh_model}</Model><Body>{body_str}</Body></Entities></SupportEntities>
  <CleanupType Value="Modify Element"/><PreserveSurfaceSkew Check="0" Value="55"/>
 </QCheck>''')

def volume_mesh(mesh_model, body_str, label, size, mtype):
    tet_type = "Tet4" if mtype == "Tet4" else "Tet10StraightEdge"
    simlab.execute(f'''<TetMesher UUID="83822e68-12bb-43b9-b2ac-77e0b9ea5149">
  <tag Value="-1"/>
  <Name Value="{label}_TetMesh_{mtype}"/>
  <SupportEntities><Entities><Model>{mesh_model}</Model><Body>{body_str}</Body></Entities></SupportEntities>
  <MeshType Value="{tet_type}"/>
  <AverageElemSize Value="{size} mm"/>
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

def merge_bodies(body_names, output_name):
    body_str = "".join(f'"{b}",' for b in body_names)
    simlab.execute(f'''<BodyMerge gda="" UUID="FA9128EE-5E6C-49af-BADF-4016E5622020">
  <tag Value="-1"/><Name Value=""/>
  <SupportEntities><Entities><Model>{MODEL}</Model><Body>{body_str}</Body></Entities></SupportEntities>
  <Delete_Shared_Faces Value="0"/>
  <Output_Body_Name Value="{output_name}"/>
  <RedoFlag Value=""/><Output/>
 </BodyMerge>''')
    print(f"  ✓ Merged → '{output_name}'")

def move_to_root(mesh_model, body_name):
    simlab.execute(f'''<MoveSubModelBodiesToRootModel UUID="0619e34b-2275-40b0-b479-882d179d560b">
  <BodiesToMove>
   <Entities>
    <Model>{mesh_model}</Model>
    <Body>"{body_name}",</Body>
   </Entities>
  </BodiesToMove>
 </MoveSubModelBodiesToRootModel>''')
    print(f"  ✓ '{body_name}' moved to root of {mesh_model}")

def get_mesh_model():
    all_models = simlab.getAllRootModelNames("all")
    return next((m for m in all_models if m != MODEL and
                 ("_SM" in m or m.endswith(".gda"))), None)

def get_actual_bodies(prefix):
    """Get current body names matching prefix from assembly."""
    root = simlab.getAllRootModelNames("all")[0]
    all_b = simlab.getChildrenInAssembly(root, root, "ALLBODIES")
    return list(dict.fromkeys([b for b in all_b if prefix in str(b)]))

# ═══════════════════════════════════════════════════════════════
# OUTER_RACE
# ═══════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  OUTER_RACE")
print("═"*60)

for body in ["OUTER_RACE", "OUTER_RACE_1"]:
    print(f"\n  ── Mesh Controls: {body} ──")
    apply_isoline(body, 13.5, 13.6, f"{body}_IsoLine_Inner", 2,   24, "0,255,255,")
    apply_isoline(body, 17.4, 17.6, f"{body}_IsoLine_Outer", 2.5, 28, "0,255,0,")

print("\n  ── Surface Mesh ──")
surface_mesh_bodies('"OUTER_RACE","OUTER_RACE_1",', mesh_size)
print("  ✓ Surface mesh done")

mesh_model = get_mesh_model()
print(f"  Mesh model: {mesh_model}")

print("\n  ── Quality Cleanup ──")
quality_cleanup(mesh_model, '"OUTER_RACE","OUTER_RACE_1",')
print("  ✓ Quality cleanup done")

print(f"\n  ── Volume Mesh ({mesh_type}) ──")
volume_mesh(mesh_model, '"OUTER_RACE","OUTER_RACE_1",', "OUTER_RACE", mesh_size, mesh_type)
print("  ✓ Volume mesh done")

print("\n  ── Merge → OUTER_RACE ──")
outer_actual = get_actual_bodies("OUTER_RACE")
print(f"  Bodies: {outer_actual}")
if len(outer_actual) >= 2:
    merge_bodies(outer_actual, "OUTER_RACE")
elif len(outer_actual) == 1:
    print(f"  Single body — already merged")

print("\n  ── Move to Root ──")
move_to_root(mesh_model, "OUTER_RACE")

# ═══════════════════════════════════════════════════════════════
# MID_RACE
# ═══════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  MID_RACE")
print("═"*60)

mid_bodies = ["MID_RACE", "MID_RACE_1", "MID_RACE_2", "MID_RACE_3"]
for body in mid_bodies:
    print(f"\n  ── Mesh Controls: {body} ──")
    apply_isoline(body, 11.4, 11.5, f"{body}_IsoLine_Inner", 2, 20, "0,255,255,")
    apply_isoline(body, 13.5, 13.6, f"{body}_IsoLine_Outer", 2, 20, "0,255,0,")

print("\n  ── Surface Mesh ──")
body_str = "".join(f'"{b}",' for b in mid_bodies)
surface_mesh_bodies(body_str, mesh_size)
print("  ✓ Surface mesh done")

mesh_model = get_mesh_model()
print(f"  Mesh model: {mesh_model}")

print("\n  ── Quality Cleanup ──")
quality_cleanup(mesh_model, body_str)
print("  ✓ Quality cleanup done")

print(f"\n  ── Volume Mesh ({mesh_type}) ──")
volume_mesh(mesh_model, body_str, "MID_RACE", mesh_size, mesh_type)
print("  ✓ Volume mesh done")

print("\n  ── Merge → MID_RACE ──")
mid_actual = get_actual_bodies("MID_RACE")
print(f"  Bodies: {mid_actual}")
if len(mid_actual) >= 2:
    merge_bodies(mid_actual, "MID_RACE")
elif len(mid_actual) == 1:
    print(f"  Single body — already merged")

print("\n  ── Move to Root ──")
move_to_root(mesh_model, "MID_RACE")

# ═══════════════════════════════════════════════════════════════
# INNER_RACE
# ═══════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  INNER_RACE")
print("═"*60)

for body in ["INNER_RACE", "INNER_RACE_1"]:
    print(f"\n  ── Mesh Controls: {body} ──")
    apply_isoline(body, 7.4,  7.6,  f"{body}_IsoLine_Inner", 2.5, 16, "0,255,255,")
    apply_isoline(body, 11.4, 11.5, f"{body}_IsoLine_Outer", 2,   20, "0,255,0,")

print("\n  ── Surface Mesh ──")
surface_mesh_bodies('"INNER_RACE","INNER_RACE_1",', mesh_size)
print("  ✓ Surface mesh done")

mesh_model = get_mesh_model()
print(f"  Mesh model: {mesh_model}")

print("\n  ── Quality Cleanup ──")
quality_cleanup(mesh_model, '"INNER_RACE","INNER_RACE_1",')
print("  ✓ Quality cleanup done")

print(f"\n  ── Volume Mesh ({mesh_type}) ──")
volume_mesh(mesh_model, '"INNER_RACE","INNER_RACE_1",', "INNER_RACE", mesh_size, mesh_type)
print("  ✓ Volume mesh done")

print("\n  ── Merge → INNER_RACE ──")
inner_actual = get_actual_bodies("INNER_RACE")
print(f"  Bodies: {inner_actual}")
if len(inner_actual) >= 2:
    merge_bodies(inner_actual, "INNER_RACE")
elif len(inner_actual) == 1:
    print(f"  Single body — already merged")

print("\n  ── Move to Root ──")
move_to_root(mesh_model, "INNER_RACE")

print("\n" + "=" * 60)
print("  All done — OUTER_RACE, MID_RACE, INNER_RACE meshed")
print("=" * 60)
