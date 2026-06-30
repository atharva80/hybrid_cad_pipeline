# -*- coding: utf-8 -*-
# =============================================================================
# SCRIPT  : mesh_pcb_bracket.py
# PURPOSE : Complete mesh workflow for PCB_BRACKET
# MESH CONTROLS:
#   1. IsoLine — Cone faces r=2.0-2.1mm, 2mm axial, 8 circ
#   2. IsoLine — Cone faces r=2.8-2.9mm, 2mm axial, 8 circ
# =============================================================================

from hwx import simlab

# -- USER INPUTS ---------------------------------------------------------------
surf_mesh_size = 3.5
vol_mesh_size  = 4
mesh_type      = "Tet4"
# -----------------------------------------------------------------------------

MODEL     = "$Geometry"
BODY_NAME = "PCB_BRACKET"

print("=" * 60)
print(f"  PCB_BRACKET — Complete Mesh Workflow")
print(f"  Surface: {surf_mesh_size}mm | Volume: {vol_mesh_size}mm | Type: {mesh_type}")
print("=" * 60)

# -- Helper: IsoLine Cone MC ---------------------------------------------------
def apply_isoline_cone(body, r_min, r_max, mc_name, axial, circ, color="0,255,0,"):
    simlab.execute(f'''<SelectFeatures UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E" CheckBox="ON">
  <SupportEntities><Entities><Model>{MODEL}</Model><Body>"{body}",</Body></Entities></SupportEntities>
  <Arcs MaxValue="0 mm" MinValue="0 mm" Value="0"/><ArcsAll Value="2"/>
  <Circles MaxValue="0 mm" MinValue="0 mm" Value="0"/><CirclesAll Value="0"/>
  <Cones MaxValue="{r_max} mm" MinValue="{r_min} mm" Value="1"/><ConeAll Value="0"/>
  <FullCone Value="1"/><ClosedPartialCone Value="1"/><OpenPartialCone Value="1"/>
  <TaperAngle Angle="0 deg" Value="0"/>
  <Dics MaxValue="0 mm" MinValue="0 mm" Value="0"/><DicsAll Value="0"/>
  <HollowDics MaxValue="0 mm" MinValue="0 mm" Value="0"/><HollowDicsAll Value="0"/>
  <Cylinders MaxValue="0 mm" MinValue="0 mm" Value="0"/><CylindersAll Value="0"/>
  <FullCylinder Value="0"/><ClosedPartialCylinder Value="0"/><OpenPartialCylinder Value="0"/>
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
        print(f"  OK {mc_name} applied")
    else:
        print(f"  - {mc_name} skipped (no faces)")

# ===============================================================
# PHASE 1: MESH CONTROLS
# ===============================================================
print("\n-- PHASE 1: Mesh Controls ----------------------------------")

print("\n[MC1] Cone faces r=2.0-2.1mm...")
apply_isoline_cone(BODY_NAME, 2.0, 2.1, "PCB_BRACKET_IsoLine_Cone1", 2, 8, "0,255,255,")

print("\n[MC2] Cone faces r=2.8-2.9mm...")
apply_isoline_cone(BODY_NAME, 2.8, 2.9, "PCB_BRACKET_IsoLine_Cone2", 2, 8, "0,255,0,")

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
                   ("_SM" in m or m.endswith(".gda"))), None)
print(f"  Mesh model: {mesh_model}")

# ===============================================================
# PHASE 3: QUALITY CHECK + CLEANUP
# ===============================================================
print("\n-- PHASE 3: Quality Check + Cleanup ------------------------")
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
print("  OK Quality cleanup done")

# ===============================================================
# PHASE 4: VOLUME MESH
# ===============================================================
print(f"\n-- PHASE 4: Volume Mesh ({mesh_type}) ----------------------")
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
print(f"  OK {mesh_type} volume mesh done")

# ===============================================================
# PHASE 5: MOVE TO ROOT
# ===============================================================
print(f"\n-- PHASE 5: Move to Root -----------------------------------")
simlab.execute(f'''<MoveSubModelBodiesToRootModel UUID="0619e34b-2275-40b0-b479-882d179d560b">
  <BodiesToMove><Entities><Model>{mesh_model}</Model><Body>"{BODY_NAME}",</Body></Entities></BodiesToMove>
 </MoveSubModelBodiesToRootModel>''')
print(f"  OK {BODY_NAME} moved to root of {mesh_model}")

print("\n" + "=" * 60)
print(f"  PCB_BRACKET complete!")
print("=" * 60)
