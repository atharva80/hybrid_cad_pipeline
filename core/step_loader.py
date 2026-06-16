"""
core/step_loader.py
====================
XCAF-aware STEP file loader.

Responsibilities:
  - Load a STEP file preserving the assembly hierarchy (XCAF labels)
  - Walk the XCAF tree and collect every TopoDS_Solid with its label metadata
  - Support renaming labels back into the document and re-exporting

Key data structure returned by extract_solids():
    List[SolidRecord] where each SolidRecord is:
    {
        "label":         TDF_Label       — XCAF label handle (for renaming)
        "label_entry":   str             — dotted label path e.g. "0:1:1:3"
        "shape":         TopoDS_Shape    — the solid geometry
        "existing_name": str | None      — name already in the XCAF tree
        "parent_entry":  str | None      — parent label entry
        "depth":         int             — depth in XCAF tree
        "is_free":       bool            — top-level free shape?
    }

Walker design:
    The walker resolves reference labels to their referred shape/sub-assembly.
    If the referred shape is itself an assembly (has XCAF children), we recurse
    into THOSE children — giving each solid its own individual label entry.
    If the referred shape is a flat compound (no XCAF children), we emit all
    solids under that one label (they share a label_entry — last rename wins).

    This correctly handles:
      - prime.STEP: deep XCAF hierarchy → each part gets a unique label ✓
      - HAMSTER: flat compound exports → best-effort, one label per compound ✓
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── OCC imports ──────────────────────────────────────────────────────────────
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Writer
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.TDF import TDF_LabelSequence, TDF_Label, TDF_Tool
from OCP.TDataStd import TDataStd_Name
from OCP.TCollection import TCollection_ExtendedString, TCollection_AsciiString
from OCP.TDocStd import TDocStd_Document
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_SHAPE, TopAbs_SHELL
from OCP.TopoDS import TopoDS, TopoDS_Shape
from OCP.BRep import BRep_Builder
from OCP.TopLoc import TopLoc_Location


# ── Data class ────────────────────────────────────────────────────────────────

@dataclass
class SolidRecord:
    label: TDF_Label
    label_entry: str
    shape: TopoDS_Shape
    existing_name: Optional[str]
    parent_entry: Optional[str]
    depth: int
    is_free: bool
    # Will be populated by feature extractor (Phase 2)
    features: dict = field(default_factory=dict)
    # Will be populated by classifier (Phase 5)
    predicted_name: Optional[str] = None
    confidence: float = 0.0


# ── Helpers ───────────────────────────────────────────────────────────────────

def _label_entry(label: TDF_Label) -> str:
    """Return the dotted string entry of a TDF label e.g. '0:1:1:3'."""
    entry = TCollection_AsciiString()
    TDF_Tool.Entry_s(label, entry)
    return entry.ToCString()


def _read_name(label: TDF_Label) -> Optional[str]:
    """Read the TDataStd_Name attribute from a label, if present."""
    name_attr = TDataStd_Name()
    if label.FindAttribute(TDataStd_Name.GetID_s(), name_attr):
        return name_attr.Get().ToExtString()
    return None


def _has_solids(shape: TopoDS_Shape) -> bool:
    """Return True if the shape contains at least one solid or shell."""
    if shape.IsNull():
        return False
    exp = TopExp_Explorer(shape, TopAbs_SOLID)
    if exp.More():
        return True
    # Fallback to shells (surfaces)
    exp_shell = TopExp_Explorer(shape, TopAbs_SHELL)
    return exp_shell.More()


def _collect_solids_from_shape(shape: TopoDS_Shape) -> list[TopoDS_Shape]:
    """Extract all TopoDS_Solid (or TopoDS_Shell) objects from a shape."""
    solids = []
    exp = TopExp_Explorer(shape, TopAbs_SOLID)
    if exp.More():
        while exp.More():
            solids.append(TopoDS.Solid(exp.Current()))
            exp.Next()
    else:
        # Fallback to shells
        exp_shell = TopExp_Explorer(shape, TopAbs_SHELL)
        while exp_shell.More():
            solids.append(TopoDS.Shell(exp_shell.Current()))
            exp_shell.Next()
    return solids


# ── Main walk ─────────────────────────────────────────────────────────────────

def _walk_label(
    label: TDF_Label,
    shape_tool: XCAFDoc_ShapeTool,
    records: list,
    parent_entry: Optional[str],
    depth: int,
    is_free: bool,
    accumulated_loc: TopLoc_Location = None
):
    """
    Recursively walk a label in the XCAF tree, preserving assembly transformations.
    """
    if accumulated_loc is None:
        accumulated_loc = TopLoc_Location()

    # Get local transformation
    local_loc = shape_tool.GetLocation_s(label)
    # Multiply parent transformation with local transformation
    current_loc = accumulated_loc.Multiplied(local_loc) if not accumulated_loc.IsIdentity() else local_loc

    entry = _label_entry(label)
    name = _read_name(label)

    # ── Step 1: Resolve reference ─────────────────────────────────────────────
    referred_label = label
    if shape_tool.IsReference_s(label):
        ref = TDF_Label()
        shape_tool.GetReferredShape_s(label, ref)
        referred_label = ref

    # ── Step 2: Check if referred label is an assembly with XCAF children ─────
    children = TDF_LabelSequence()
    shape_tool.GetComponents_s(referred_label, children, False)
    has_xcaf_children = children.Length() > 0

    # ── Step 3a: Assembly with children → recurse into children ───────────────
    if has_xcaf_children:
        for i in range(children.Length()):
            child = children.Value(i + 1)
            _walk_label(child, shape_tool, records, entry, depth + 1, False, current_loc)
        return

    # ── Step 3b: Also recurse if the label itself is an assembly ──────────────
    if shape_tool.IsAssembly_s(label):
        direct_children = TDF_LabelSequence()
        shape_tool.GetComponents_s(label, direct_children, False)
        for i in range(direct_children.Length()):
            child = direct_children.Value(i + 1)
            _walk_label(child, shape_tool, records, entry, depth + 1, False, current_loc)
        return

    # ── Step 4: Leaf node — emit SolidRecords ────────────────────────────────
    shape = shape_tool.GetShape_s(referred_label)
    if shape is None or shape.IsNull():
        return

    # Apply the accumulated global transformation to the leaf shape
    if not current_loc.IsIdentity():
        shape.Location(current_loc)

    if _has_solids(shape):
        solids = _collect_solids_from_shape(shape)
        for solid in solids:
            records.append(
                SolidRecord(
                    label=label,
                    label_entry=entry,
                    shape=solid,
                    existing_name=name,
                    parent_entry=parent_entry,
                    depth=depth,
                    is_free=is_free,
                )
            )


# ── Public API ────────────────────────────────────────────────────────────────

def load_step_xcaf(filepath: str | Path) -> tuple[TDocStd_Document, XCAFDoc_ShapeTool]:
    """
    Load a STEP file into an XCAF document.

    Returns:
        (doc, shape_tool)
        doc:        TDocStd_Document  — the live XCAF document
        shape_tool: XCAFDoc_ShapeTool — handle for tree traversal and renaming

    Raises:
        RuntimeError if the file cannot be read.
    """
    filepath = str(filepath)
    doc = TDocStd_Document(TCollection_ExtendedString("MDTV-Standard"))
    reader = STEPCAFControl_Reader()
    reader.SetNameMode(True)   # preserve part names
    reader.SetColorMode(True)
    reader.SetLayerMode(True)

    status = reader.ReadFile(filepath)
    if status != 1:
        raise RuntimeError(
            f"STEPCAFControl_Reader failed on '{filepath}' (status={status})"
        )

    ok = reader.Transfer(doc)
    if not ok:
        raise RuntimeError(f"XCAF transfer failed for '{filepath}'")

    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    return doc, shape_tool


def extract_solids(shape_tool: XCAFDoc_ShapeTool) -> list[SolidRecord]:
    """
    Walk the XCAF tree and return a flat list of SolidRecord for every solid found.

    Solids from the same compound leaf node share the same label_entry.
    Solids from distinct XCAF-parented shapes each get a unique label_entry.
    """
    records: list[SolidRecord] = []
    free_labels = TDF_LabelSequence()
    shape_tool.GetFreeShapes(free_labels)

    for i in range(free_labels.Length()):
        label = free_labels.Value(i + 1)
        _walk_label(label, shape_tool, records, None, 0, True)

    # Deduplicate by (label_entry, shape identity)
    seen = set()
    unique: list[SolidRecord] = []
    for rec in records:
        key = (rec.label_entry, id(rec.shape))
        if key not in seen:
            seen.add(key)
            unique.append(rec)

    return unique


def rename_label(label: TDF_Label, new_name: str) -> None:
    """
    Set TDataStd_Name on a label AND on its referred shape definition.

    FreeCAD (and most CAD tools) display the PRODUCT (definition) name,
    not the NEXT_ASSEMBLY_USAGE_OCCURRENCE (instance) name.
    Writing to both ensures the name appears in all viewers.
    """
    TDataStd_Name.Set_s(label, TCollection_ExtendedString(new_name))
    # Also rename the referred shape definition (PRODUCT entity in STEP)
    try:
        root_lbl = label.Root()
        st = XCAFDoc_DocumentTool.ShapeTool_s(root_lbl)
        if st.IsReference_s(label):
            ref = TDF_Label()
            st.GetReferredShape_s(label, ref)
            # Write base name (strip sequential suffix _NN) to the definition
            base = new_name.rstrip("0123456789").rstrip("_")
            TDataStd_Name.Set_s(ref, TCollection_ExtendedString(base if base else new_name))
    except Exception:
        pass


def export_step(doc: TDocStd_Document, output_path: str | Path) -> None:
    """
    Export the modified XCAF document back to a STEP file.

    Raises:
        RuntimeError if export fails.
    """
    output_path = str(output_path)
    writer = STEPCAFControl_Writer()
    writer.SetNameMode(True)
    writer.SetColorMode(True)

    ok = writer.Transfer(doc)
    if not ok:
        raise RuntimeError("STEPCAFControl_Writer.Transfer() failed")

    status = writer.Write(output_path)
    if status != 1:
        raise RuntimeError(f"STEPCAFControl_Writer.Write() failed (status={status})")


def apply_names(
    doc: TDocStd_Document,
    assignments: list[tuple[TDF_Label, str]],
    output_path: str | Path,
) -> None:
    """
    Convenience wrapper: rename labels then export.

    Args:
        doc:         The live XCAF document.
        assignments: List of (label, new_name) pairs.
        output_path: Where to write the output STEP file.
    """
    for label, name in assignments:
        rename_label(label, name)
    export_step(doc, output_path)
