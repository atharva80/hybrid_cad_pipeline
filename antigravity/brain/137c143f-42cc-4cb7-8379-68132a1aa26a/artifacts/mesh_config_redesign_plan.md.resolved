# Mesh Config Redesign Plan
## From: Hardcoded Template Injection → To: JSON-Driven Parameter Config Panel

---

## The Core Problem with the Current Design

Right now, `_handle_mesh()` works like this:
1. Reads `mesh_races.py` into memory as a **raw string**.
2. Regex-patches `BODY_NAME`, `mesh_size`, and CSV paths blindly.
3. Sends the whole patched string over TCP.

**Why this is fragile:**
- You can only change what you can predict with regex. If the template has a hardcoded `axial_size=2` or `cir_elems=24` buried in a function call, there is no way to expose that to the user.
- The template is the source of truth, meaning any user-facing control is just faking it — the real knobs are inside an opaque Python file.
- No validation. If a user types `abc` as a mesh size, it fails inside SimLab with no useful feedback.

---

## The New Architecture: JSON Mesh Config

### Key Idea
Instead of treating `mesh_races.py` as the **data + logic** combined, we separate them:
- **Logic stays in the `.py` template** (the SimLab API calls — don't touch these).
- **All tunable values move to a companion `.json` config file**.

The ATLAS UI reads the JSON to populate a config panel. The user edits values in the panel. When they click Mesh, the app reads the JSON values and injects them directly — no regex guessing.

---

## New File Structure

```
EXISTING_SCRIPTS/
└── MESHING/
    ├── mesh_shaft.py              ← logic only (reads params from args/env)
    ├── mesh_shaft.json            ← all tunable params for SHAFT
    ├── mesh_races.py
    ├── mesh_races.json
    ├── mesh_stator.py
    ├── mesh_stator.json
    ├── mesh_rotor_ring.py
    ├── mesh_rotor_ring.json
    ├── mesh_top_cover_complete.py
    ├── mesh_top_cover_complete.json
    ├── mesh_bottom_cover.py
    ├── mesh_bottom_cover.json
    ├── mesh_body.py
    ├── mesh_body.json
    ├── mesh_pcb_bracket.py
    ├── mesh_pcb_bracket.json
    └── mesh_display_pcb.py
        mesh_display_pcb.json
```

---

## JSON Config Format

Each `.json` has a standard schema with clearly named sections:

```json
{
  "component": "SHAFT",
  "description": "Complete mesh workflow for motor shaft with stator seating controls",
  "global": {
    "mesh_size": { "value": 4.0, "unit": "mm", "min": 1.0, "max": 10.0, "label": "Surface/Volume Mesh Size" },
    "mesh_type": { "value": "Tet4", "options": ["Tet4", "Tet10"], "label": "Element Type" }
  },
  "mesh_controls": [
    {
      "name": "SHAFT_IsoLine_InnerRace",
      "type": "IsoLine_Cylinder",
      "label": "Inner Race Seating",
      "params": {
        "r_min": { "value": 7.4, "unit": "mm", "label": "Radius Min" },
        "r_max": { "value": 7.6, "unit": "mm", "label": "Radius Max" },
        "axial_size": { "value": 2.5, "unit": "mm", "label": "Axial Element Size" },
        "cir_elems": { "value": 16, "unit": "count", "label": "Circumferential Elements" }
      }
    },
    {
      "name": "SHAFT_IsoLine_Stator",
      "type": "IsoLine_Cylinder",
      "label": "Stator Seating",
      "params": {
        "r_min": { "value": 7.7, "unit": "mm", "label": "Radius Min" },
        "r_max": { "value": 7.75, "unit": "mm", "label": "Radius Max" },
        "axial_size": { "value": 2.0, "unit": "mm", "label": "Axial Element Size" },
        "cir_elems": { "value": 6, "unit": "count", "label": "Circumferential Elements" }
      }
    }
  ],
  "quality": {
    "aspect_ratio_limit": { "value": 10.0, "label": "Max Aspect Ratio" },
    "min_edge_length": { "value": 0.25, "unit": "mm", "label": "Min Edge Length" },
    "min_height": { "value": 0.2, "unit": "mm", "label": "Min Element Height" }
  },
  "volume": {
    "internal_grading": { "value": 2.0, "label": "Internal Grading" },
    "min_quality": { "value": 0.12, "label": "Min Tet Quality" }
  }
}
```

---

## How Dispatch Changes

Instead of regex injection, `_handle_mesh()` will:
1. Read the JSON config for the component.
2. Apply any user edits (from the Config Panel) on top of the JSON defaults.
3. Pass the final JSON dict as the payload — **not raw Python code**.

```json
{
  "script": "mesh_shaft",
  "body_name": "SHAFT",
  "params": {
    "mesh_size": 4.0,
    "mesh_type": "Tet10",
    "mesh_controls": [
      { "name": "SHAFT_IsoLine_InnerRace", "r_min": 7.4, "r_max": 7.6, "axial_size": 2.5, "cir_elems": 16 },
      { "name": "SHAFT_IsoLine_Stator",    "r_min": 7.7, "r_max": 7.75, "axial_size": 2.0, "cir_elems": 6 }
    ],
    "quality": { "aspect_ratio_limit": 10.0, "min_edge_length": 0.25, "min_height": 0.2 },
    "volume":  { "internal_grading": 2.0, "min_quality": 0.12 }
  }
}
```

On the **SimLab side**, `simlab_api_server.py` unpacks this JSON and calls into the `.py` template passing params as arguments — zero regex, zero guessing.

---

## UI: Component Config Side Panel

When the user clicks a **component name** in the Meshing Tab table:

```
┌─────────────────────────────────────────────────────────┐
│  ← SHAFT  —  Mesh Configuration                         │
├──────────────────────────┬──────────────────────────────┤
│  GLOBAL                  │                              │
│  Mesh Size (mm)  [ 4.0 ] │                              │
│  Element Type  [Tet4 ▾]  │                              │
├──────────────────────────┤   Live Preview               │
│  MESH CONTROLS           │   (render thumbnail of       │
│  ▾ Inner Race Seating    │    component from ATLAS)     │
│    r_min:  [ 7.4 ] mm    │                              │
│    r_max:  [ 7.6 ] mm    │                              │
│    Axial:  [ 2.5 ] mm    │                              │
│    Circ:   [ 16  ] elems │                              │
│  ▾ Stator Seating        │                              │
│    r_min:  [ 7.7 ] mm    │                              │
│    r_max:  [7.75 ] mm    │                              │
│    Axial:  [ 2.0 ] mm    │                              │
│    Circ:   [  6  ] elems │                              │
├──────────────────────────┤                              │
│  QUALITY                 │                              │
│  Max Aspect Ratio [ 10 ] │                              │
│  Min Edge (mm) [ 0.25 ]  │                              │
├──────────────────────────┴──────────────────────────────┤
│  [Reset to Defaults]          [Save Config]  [▶ Mesh]   │
└─────────────────────────────────────────────────────────┘
```

- **Reset to Defaults** loads the values back from the `.json` file.
- **Save Config** writes the edited values back to the `.json` file (persists across sessions!).
- **▶ Mesh** dispatches the current panel values to SimLab via TCP.

---

## Implementation Steps (Phased)

### Phase 1 — Schema & JSON Files *(Low Risk)*
- [ ] Write `.json` config files for all 9 components using the schema above.
- [ ] Validate schema is complete and covers every hardcoded value in the `.py` templates.

### Phase 2 — SimLab-Side Script Refactor *(Medium Risk)*
- [ ] Refactor `.py` templates to **accept a `params` dict** instead of hardcoded top-level variables.
- [ ] The server unpacks JSON payload and calls `mesh_shaft.run(body_name, params)`.
- [ ] Keep the SimLab XML generation logic identical — only the data source changes.

### Phase 3 — ATLAS Config Panel UI *(Medium Effort)*
- [ ] Add `MeshConfigPanel` widget as a right-side drawer in the Meshing Tab.
- [ ] Clicking a component name in the table opens/slides in the config panel.
- [ ] Panel dynamically builds form fields from the JSON schema (no hardcoded UI).
- [ ] Implement Save Config and Reset to Defaults.

### Phase 4 — Connect Dispatch *(Low Risk)*
- [ ] Replace `_handle_mesh()` regex injection with JSON-serialized dispatch.
- [ ] Update `simlab_api_server.py` to receive structured JSON, not raw code strings.
- [ ] Remove all regex patching code.

---

## Design Decisions to Confirm

> [!IMPORTANT]
> Before starting implementation, confirm these decisions:

1. **Should "Save Config" be per-project or global?**  
   *Option A:* Save back to `EXISTING_SCRIPTS/MESHING/*.json` (global, affects all future uses).  
   *Option B:* Save to `_run_history/<session>/mesh_configs/*.json` (per-session, preserves originals).

2. **Should the JSON schema be flat or nested?**  
   Nested (as designed above) gives cleaner grouping but requires a recursive UI builder.

3. **Is the component render thumbnail feasible?**  
   We already generate component renders during inference. We can reuse those images in the panel.

4. **Do the `.py` templates get refactored, or does the server adapt?**  
   Cleaner long-term to refactor templates (Phase 2), but if time-constrained, the server can still inject params into the top of the script string (smarter than current regex, but still string-based).
