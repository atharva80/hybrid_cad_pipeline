import glob

files = glob.glob("/mnt/f/02.CAE/ATHARVA/hybrid_cad_pipeline/mesh_templates/*.py")

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    modified = False
    
    # Add OK Surface mesh done
    if "simlab.execute(SurfaceMesh)" in content and "OK Surface mesh done" not in content:
        content = content.replace("simlab.execute(SurfaceMesh)", 'simlab.execute(SurfaceMesh)\n    print("  OK Surface mesh done")')
        modified = True
        
    # Add OK volume mesh done
    if "simlab.execute(TetMesh)" in content and "volume mesh done" not in content:
        content = content.replace("simlab.execute(TetMesh)", 'simlab.execute(TetMesh)\n        print(f"  OK {mesh_type} volume mesh done")')
        modified = True
        
    if "simlab.execute(HexMesh)" in content and "Hex volume mesh done" not in content:
        content = content.replace("simlab.execute(HexMesh)", 'simlab.execute(HexMesh)\n        print("  OK Hex volume mesh done")')
        modified = True
        
    if "BODY_NAME} complete!" not in content:
        if "simlab.execute(HexMesh)" in content:
            # Append to the end of the file
            content += '\n    print(f"\\n============================================================")\n    print(f"  {BODY_NAME} complete!")\n    print(f"============================================================")\n'
            modified = True
            
    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Added prints to {filepath}")

