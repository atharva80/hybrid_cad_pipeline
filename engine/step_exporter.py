#!/usr/bin/env python3
"""
step_exporter.py
================
Flattens the entire CAD assembly and writes a new STEP file where the
messy hierarchy is destroyed. Every solid becomes a direct child of the root.

Identified parts are named with their component class (e.g. "STATOR", "TOP_COVER").
All remaining (unclassified) parts are named "Solid_0", "Solid_1", etc.

Output filename: {original_name}_NAMED.step
"""

import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder


def export_named_step(inference_output: dict, out_dir: str, original_step_path: str) -> str:
    """
    Creates a brand new flattened XCAF document and exports it as a STEP file.
    """
    os.makedirs(out_dir, exist_ok=True)

    basename    = os.path.splitext(os.path.basename(original_step_path))[0]
    output_path = os.path.join(out_dir, f"{basename}_NAMED.step")

    records = inference_output["records"]
    results = inference_output["results"]

    # Build mapping of node_idx -> Component Name
    assigned: dict[int, str] = {}
    for comp, nodes, _ in results:
        counts: dict[str, int] = {}
        for node in nodes:
            if node is None or node in assigned:
                continue
            if len([n for n in nodes if n is not None]) > 1:
                counts[comp] = counts.get(comp, 0) + 1
                new_name = f"{comp}_{counts[comp]}"
            else:
                new_name = comp
            assigned[node] = new_name

    # Create new flat document
    new_doc = TDocStd_Document(TCollection_ExtendedString("MDTV-Standard"))
    new_st  = XCAFDoc_DocumentTool.ShapeTool_s(new_doc.Main())

    # Build a compound holding all solids, explicitly copying them 
    # to break any shared definitions (which causes XCAF instancing bugs)
    comp = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(comp)

    from OCP.BRepBuilderAPI import BRepBuilderAPI_Copy

    print(f"\n  🔨 Flattening {len(records)} solids into new assembly...")
    for r in records:
        copied_shape = BRepBuilderAPI_Copy(r.shape).Shape()
        builder.Add(comp, copied_shape)

    # Add the compound as the root assembly
    root_lbl = new_st.AddShape(comp, True)  # makeAssembly=True
    TDataStd_Name.Set_s(root_lbl, TCollection_ExtendedString(basename))

    # Extract all the flattened components (direct children)
    components = TDF_LabelSequence()
    new_st.GetComponents_s(root_lbl, components)

    # Rename them
    for i in range(components.Length()):
        comp_lbl = components.Value(i + 1)
        node_idx = i  # The order matches exactly how we added them
        
        if node_idx in assigned:
            name = assigned[node_idx]
            print(f"  ✏️  Solid #{node_idx} → {name}")
        else:
            name = f"Solid_{node_idx}"

        TDataStd_Name.Set_s(comp_lbl, TCollection_ExtendedString(name))
        
        # Also rename the referred shape definition
        if new_st.IsReference_s(comp_lbl):
            ref_lbl = TDF_Label()
            new_st.GetReferredShape_s(comp_lbl, ref_lbl)
            TDataStd_Name.Set_s(ref_lbl, TCollection_ExtendedString(name))

    # Export
    writer = STEPCAFControl_Writer()
    writer.SetNameMode(True)
    writer.SetColorMode(True)

    ok = writer.Transfer(new_doc)
    if not ok:
        print("  ❌ STEPCAFControl_Writer.Transfer failed")
        return ""

    status = writer.Write(output_path)
    if status == IFSelect_RetDone:
        print(f"  ✅ Exported Flattened NAMED STEP → {output_path}")
    else:
        print(f"  ❌ STEP export failed (status code: {status})")

    return output_path
