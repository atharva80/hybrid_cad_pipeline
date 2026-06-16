"""
core/feature_extractor.py
===========================
Per-solid geometric feature extraction — Phase 2.

All features are scale-invariant (ratios / percentages / counts).
No absolute mm thresholds here — those live in the templates YAML.

Feature vector per solid (all dimensionless unless noted):
  Surface distribution:
    pct_plane, pct_cylinder, pct_cone, pct_sphere,
    pct_torus, pct_bspline, pct_other         — fraction of total faces
    face_count                                 — raw count (not scale-invariant,
                                                 but critical for stator detection)
  Shape ratios:
    aspect_min_max   = d_min / d_max           — 0=flat/thin, 1=cube
    aspect_mid_max   = d_mid / d_max           — 0=elongated, 1=square cross-section
    flatness_index   = d_min / d_mid           — 1.0=circular x-section (shaft),
                                                 <<1=disc (stator)
  Cylinder geometry:
    cylindricity_index = (max_r - min_r) / max_r   — 0=solid, 1=thin ring
    has_hollow_cylinder                         — 1.0 if multiple distinct radii
    max_cyl_radius_mm  (mm — reference only)
    min_cyl_radius_mm  (mm — reference only)
    head_to_body_ratio = max_r / min_r         — bolt head discrimination
  Sphere geometry:
    max_sphere_radius_mm (mm — reference only)
  Mass properties:
    volume_mm3       (mm³ — reference only)
    surface_area_mm2 (mm² — reference only)
    compactness      = volume / surface_area^1.5   — compact blob vs thin shell
  Spatial:
    bbox_center      = (cx, cy, cz) mm          — for edge detection in Phase 3
    center_of_mass   = (cx, cy, cz) mm          — for edge detection in Phase 3
    dim_min_mm, dim_mid_mm, dim_max_mm (mm)     — raw dims, for spatial checks
"""

from __future__ import annotations
from collections import defaultdict
from typing import Optional

from OCP.BRepGProp import BRepGProp
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.Bnd import Bnd_Box
from OCP.GProp import GProp_GProps
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS, TopoDS_Shape
from OCP.GeomAbs import (
    GeomAbs_Plane, GeomAbs_Cylinder, GeomAbs_Cone,
    GeomAbs_Sphere, GeomAbs_Torus,
    GeomAbs_BSplineSurface, GeomAbs_BezierSurface,
    GeomAbs_SurfaceOfRevolution, GeomAbs_SurfaceOfExtrusion,
    GeomAbs_OffsetSurface, GeomAbs_OtherSurface,
)

# ── Surface type → label map ──────────────────────────────────────────────────
_SURF_LABEL = {
    GeomAbs_Plane: "plane",
    GeomAbs_Cylinder: "cylinder",
    GeomAbs_Cone: "cone",
    GeomAbs_Sphere: "sphere",
    GeomAbs_Torus: "torus",
    GeomAbs_BSplineSurface: "bspline",
    GeomAbs_BezierSurface: "bspline",      # treat bezier same as bspline
    GeomAbs_SurfaceOfRevolution: "other",
    GeomAbs_SurfaceOfExtrusion: "other",
    GeomAbs_OffsetSurface: "other",
    GeomAbs_OtherSurface: "other",
}
_SURFACE_KEYS = ["plane", "cylinder", "cone", "sphere", "torus", "bspline", "other"]


# ── T2.1 Surface distribution ─────────────────────────────────────────────────

def get_surface_distribution(solid: TopoDS_Shape) -> dict:
    """
    Classify every face of the solid by surface type.

    Returns:
        {
          "pct_plane": float, "pct_cylinder": float, "pct_cone": float,
          "pct_sphere": float, "pct_torus": float, "pct_bspline": float,
          "pct_other": float, "face_count": int,
          "_cyl_radii": [float, ...],    # raw cylinder radii (mm) for T2.3
          "_sph_radii": [float, ...],    # raw sphere radii (mm)
        }
    """
    counts = defaultdict(int)
    cyl_radii: list[float] = []
    sph_radii: list[float] = []
    total = 0

    exp = TopExp_Explorer(solid, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face(exp.Current())
        try:
            surf = BRepAdaptor_Surface(face, True)
            st = surf.GetType()
            label = _SURF_LABEL.get(st, "other")
            counts[label] += 1

            if st == GeomAbs_Cylinder:
                cyl_radii.append(surf.Cylinder().Radius())
            elif st == GeomAbs_Sphere:
                sph_radii.append(surf.Sphere().Radius())
        except Exception:
            counts["other"] += 1
        total += 1
        exp.Next()

    if total == 0:
        # degenerate shape — return zeros
        result = {f"pct_{k}": 0.0 for k in _SURFACE_KEYS}
        result["face_count"] = 0
        result["_cyl_radii"] = []
        result["_sph_radii"] = []
        return result

    result = {f"pct_{k}": round(counts.get(k, 0) / total, 6) for k in _SURFACE_KEYS}
    result["face_count"] = total
    result["_cyl_radii"] = cyl_radii
    result["_sph_radii"] = sph_radii
    return result


# ── T2.2 Shape ratios ─────────────────────────────────────────────────────────

def get_shape_ratios(solid: TopoDS_Shape) -> dict:
    """
    Compute bounding-box-derived shape ratios.

    Returns:
        {
          "aspect_min_max": float,  "aspect_mid_max": float,
          "flatness_index": float,
          "dim_min_mm": float, "dim_mid_mm": float, "dim_max_mm": float,
          "bbox_center": (float, float, float),
          "_bbox": (xmin,ymin,zmin,xmax,ymax,zmax),
        }
    Returns None values on degenerate shape.
    """
    bbox = Bnd_Box()
    BRepBndLib.Add_s(solid, bbox)

    if bbox.IsVoid():
        return {
            "aspect_min_max": 0.0, "aspect_mid_max": 0.0, "flatness_index": 0.0,
            "dim_min_mm": 0.0, "dim_mid_mm": 0.0, "dim_max_mm": 0.0,
            "bbox_center": (0.0, 0.0, 0.0),
            "_bbox": (0,)*6,
        }

    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    raw = [xmax - xmin, ymax - ymin, zmax - zmin]
    d_min, d_mid, d_max = sorted(raw)

    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2
    cz = (zmin + zmax) / 2

    aspect_min_max = round(d_min / d_max, 6) if d_max > 0 else 0.0
    aspect_mid_max = round(d_mid / d_max, 6) if d_max > 0 else 0.0
    flatness_index = round(d_min / d_mid, 6) if d_mid > 0 else 1.0

    return {
        "aspect_min_max": aspect_min_max,
        "aspect_mid_max": aspect_mid_max,
        "flatness_index": flatness_index,
        "dim_min_mm": round(d_min, 4),
        "dim_mid_mm": round(d_mid, 4),
        "dim_max_mm": round(d_max, 4),
        "bbox_center": (round(cx, 4), round(cy, 4), round(cz, 4)),
        "_bbox": (xmin, ymin, zmin, xmax, ymax, zmax),
    }


# ── T2.3 Cylindricity ─────────────────────────────────────────────────────────

def get_cylindricity(cyl_radii: list[float]) -> dict:
    """
    Compute cylinder-radius-derived features from the radii collected in T2.1.

    Returns:
        {
          "cylindricity_index": float,  "has_hollow_cylinder": float,
          "max_cyl_radius_mm": float,   "min_cyl_radius_mm": float,
          "head_to_body_ratio": float,
          "_cyl_radii_unique": [float],  # rounded unique radii
        }
    """
    if not cyl_radii:
        return {
            "cylindricity_index": 0.0, "has_hollow_cylinder": 0.0,
            "max_cyl_radius_mm": 0.0, "min_cyl_radius_mm": 0.0,
            "head_to_body_ratio": 1.0,
            "_cyl_radii_unique": [],
        }

    max_r = max(cyl_radii)
    min_r = min(cyl_radii)
    uniq = sorted(set(round(r, 1) for r in cyl_radii))

    cylindricity_index = round((max_r - min_r) / max_r, 6) if max_r > 0 else 0.0
    has_hollow = 1.0 if len(uniq) > 1 else 0.0
    head_to_body = round(max_r / min_r, 4) if min_r > 0 else 1.0

    return {
        "cylindricity_index": cylindricity_index,
        "has_hollow_cylinder": has_hollow,
        "max_cyl_radius_mm": round(max_r, 4),
        "min_cyl_radius_mm": round(min_r, 4),
        "head_to_body_ratio": head_to_body,
        "_cyl_radii_unique": uniq,
    }


# ── T2.4 Mass properties ──────────────────────────────────────────────────────

def get_mass_props(solid: TopoDS_Shape) -> dict:
    """
    Compute volume, surface area, compactness and centre of mass.

    Returns:
        {
          "volume_mm3": float, "surface_area_mm2": float,
          "compactness": float, "center_of_mass": (float, float, float),
        }
    """
    try:
        vp = GProp_GProps()
        BRepGProp.VolumeProperties_s(solid, vp)
        volume = vp.Mass()

        sp = GProp_GProps()
        BRepGProp.SurfaceProperties_s(solid, sp)
        surface_area = sp.Mass()

        com = vp.CentreOfMass()
        compactness = (
            round(volume / (surface_area ** 1.5), 8) if surface_area > 0 else 0.0
        )

        return {
            "volume_mm3": round(volume, 4),
            "surface_area_mm2": round(surface_area, 4),
            "compactness": compactness,
            "center_of_mass": (
                round(com.X(), 4), round(com.Y(), 4), round(com.Z(), 4)
            ),
        }
    except Exception:
        return {
            "volume_mm3": 0.0, "surface_area_mm2": 0.0,
            "compactness": 0.0, "center_of_mass": (0.0, 0.0, 0.0),
        }


# ── T2.5 Public aggregator ────────────────────────────────────────────────────

def extract_features(solid: TopoDS_Shape) -> dict:
    """
    Compute the complete feature vector for a single solid.

    Returns a flat dict ready to be stored as node attributes in the graph.
    Internal keys starting with '_' are kept for Phase 3 but not used
    in template matching.

    Returns {} on degenerate (zero-face) solid.
    """
    surf = get_surface_distribution(solid)
    if surf["face_count"] == 0:
        return {}

    ratios = get_shape_ratios(solid)
    cyl = get_cylindricity(surf["_cyl_radii"])
    mass = get_mass_props(solid)

    # Sphere radii summary (for bearing ball detection)
    sph_radii = surf.get("_sph_radii", [])
    max_sph_r = round(max(sph_radii), 4) if sph_radii else 0.0

    # Build flat output — strip private keys, add them back cleanly
    features = {}
    # Surface
    for k in _SURFACE_KEYS:
        features[f"pct_{k}"] = surf[f"pct_{k}"]
    features["face_count"] = surf["face_count"]
    # Radii lists (needed by graph builder)
    features["_cyl_radii"] = surf["_cyl_radii"]
    features["_cyl_radii_unique"] = cyl["_cyl_radii_unique"]
    features["_sph_radii"] = sph_radii
    features["_bbox"] = ratios["_bbox"]
    # Shape ratios
    features["aspect_min_max"] = ratios["aspect_min_max"]
    features["aspect_mid_max"] = ratios["aspect_mid_max"]
    features["flatness_index"] = ratios["flatness_index"]
    features["dim_min_mm"] = ratios["dim_min_mm"]
    features["dim_mid_mm"] = ratios["dim_mid_mm"]
    features["dim_max_mm"] = ratios["dim_max_mm"]
    features["bbox_center"] = ratios["bbox_center"]
    # Cylindricity
    features["cylindricity_index"] = cyl["cylindricity_index"]
    features["has_hollow_cylinder"] = cyl["has_hollow_cylinder"]
    features["max_cyl_radius_mm"] = cyl["max_cyl_radius_mm"]
    features["min_cyl_radius_mm"] = cyl["min_cyl_radius_mm"]
    features["head_to_body_ratio"] = cyl["head_to_body_ratio"]
    # Sphere
    features["max_sphere_radius_mm"] = max_sph_r
    # Mass
    features["volume_mm3"] = mass["volume_mm3"]
    features["surface_area_mm2"] = mass["surface_area_mm2"]
    features["compactness"] = mass["compactness"]
    features["center_of_mass"] = mass["center_of_mass"]

    return features


def extract_all(records) -> None:
    """
    In-place: populate the .features dict on every SolidRecord in the list.
    Skips records that already have features (idempotent).
    """
    for rec in records:
        if not rec.features:
            rec.features = extract_features(rec.shape)
