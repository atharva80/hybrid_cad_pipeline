import os, glob, re

template_dir = "/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates"
files = glob.glob(os.path.join(template_dir, "mesh_*.py"))

for f in sorted(files):
    name = os.path.basename(f)
    content = open(f).read()
    
    is_atomic = "Atomic" in content or "Bypassed Standalone Surface Mesh" in content or "<SurfaceMesh" not in content
    has_surface = "<SurfaceMesh" in content
    has_volume = "<TetMesher" in content or "<AutoHexMesh" in content
    
    mc_tags = []
    if "IsoLine" in content: mc_tags.append("IsoLine")
    if "Logo" in content: mc_tags.append("Logo/Defeature")
    if "RemoveHole" in content or "Remove Holes" in content: mc_tags.append("Remove Holes")
    if "MergeFaces" in content: mc_tags.append("Merge Faces (Layer Change)")
    
    print(f"--- {name} ---")
    if is_atomic and not has_surface:
        print("  Type: Atomic (Direct CAD Volume Mesh)")
    elif has_surface and has_volume:
        print("  Type: Surface Mesh -> Quality Cleanup -> Volume Mesh")
    elif has_surface:
        print("  Type: Surface Mesh Only")
    else:
        print("  Type: Custom / Unknown")
        
    if mc_tags:
        print(f"  Mesh Controls: {', '.join(mc_tags)}")
    else:
        print("  Mesh Controls: None")
    print("")

