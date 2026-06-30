# =============================================================================
# SCRIPT  : mesh_rotor_ring.py
# PURPOSE : Complete mesh workflow for ROTOR_RING
#           No mesh controls — direct surface mesh
# =============================================================================

from hwx import simlab

# ── USER INPUTS ───────────────────────────────────────────────────────────────
surf_mesh_size = 4.5
vol_mesh_size  = 5
mesh_type      = "Tet4"
# ─────────────────────────────────────────────────────────────────────────────

MODEL     = "$Geometry"
BODY_NAME = "ROTOR_RING"

print("=" * 60)
print(f"  ROTOR_RING — Complete Mesh Workflow")
print(f"  Surface: {surf_mesh_size}mm | Volume: {vol_mesh_size}mm | Type: {mesh_type}")
print("=" * 60)

# ═══════════════════════════════════════════════════════════════
# PHASE 1: SURFACE MESH
# ═══════════════════════════════════════════════════════════════
print("\n── PHASE 1: Surface Mesh ───────────────────────────────────")
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
print("  ✓ Surface mesh done")

all_models = simlab.getAllRootModelNames("all")
mesh_model = next((m for m in all_models if m != MODEL and
                   ("_SM" in m or m.endswith(".gda"))), None)
print(f"  Mesh model: {mesh_model}")

# ═══════════════════════════════════════════════════════════════
# PHASE 2: QUALITY CHECK + CLEANUP
# ═══════════════════════════════════════════════════════════════
print("\n── PHASE 2: Quality Check + Cleanup ────────────────────────")
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
# PHASE 3: VOLUME MESH
# ═══════════════════════════════════════════════════════════════
print(f"\n── PHASE 3: Volume Mesh ({mesh_type}) ──────────────────────")
tet_type = "Tet4" if mesh_type == "Tet4" else "Tet10StraightEdge"
simlab.execute(f'''<TetMesher UUID="83822e68-12bb-43b9-b2ac-77e0b9ea5149">
  <tag Value="-1"/>
  <Name Value="{BODY_NAME}_TetMesh_{mesh_type}"/>
  <SupportEntities><Entities><Model>{mesh_model}</Model><Body>"{BODY_NAME}",</Body></Entities></SupportEntities>
  <MeshType Value="{tet_type}"/>
  <AverageElemSize Value="{vol_mesh_size} mm"/>
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
# PHASE 4: MOVE TO ROOT
# ═══════════════════════════════════════════════════════════════
print(f"\n── PHASE 4: Move to Root ───────────────────────────────────")
simlab.execute(f'''<MoveSubModelBodiesToRootModel UUID="0619e34b-2275-40b0-b479-882d179d560b">
  <BodiesToMove><Entities><Model>{mesh_model}</Model><Body>"{BODY_NAME}",</Body></Entities></BodiesToMove>
 </MoveSubModelBodiesToRootModel>''')
print(f"  ✓ {BODY_NAME} moved to root of {mesh_model}")

print("\n" + "=" * 60)
print(f"  ROTOR_RING complete!")
print("=" * 60)
