# Contact Tab Implementation & Rules Plan

As requested, I will not write any code until this plan is finalized. 

Below is the structured plan for the Contacts Tab feature, including the default parameters and the auto-suggested contact pairs based on the ATLAS hybrid CAD assembly.

## Default Parameters
- **Default Tolerance**: `0.05 mm`
- **Default Solver**: `Radioss`
- **Default Contact Type**: `Friction (Type24)`
- **Default Face Type**: `All`
- **Default Friction Coefficient**: `0.1`

## Auto-Suggested Contact Pairs
When a CAD assembly is parsed, ATLAS will cross-reference the identified components. If it finds the components listed below, it will automatically suggest these contact pairs in the Contacts Tab table. 

*(Note: Master/Slave assignments generally place the larger/stiffer/stationary body as the Master, but this can be adjusted in the UI).*

| Suggested Contact Pair | Master Body | Slave Body | Contact Type | Face Type | Tolerance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Shaft to Stator** | `SHAFT` | `STATOR` | `Friction (Type24)` | All | `0.05 mm` |
| **Shaft to Top Bearing** | `SHAFT` | `BEARING_TOP_INNER` | `Friction (Type24)` | All | `0.05 mm` |
| **Shaft to Bottom Bearing** | `SHAFT` | `BEARING_BOTTOM_INNER` | `Friction (Type24)` | All | `0.05 mm` |
| **Top Bearing to Top Cover** | `TOP_COVER` | `BEARING_TOP_OUTER` | `Friction (Type24)` | All | `0.05 mm` |
| **Bottom Bearing to Bottom Cover** | `BOTTOM_COVER` | `BEARING_BOTTOM_OUTER` | `Friction (Type24)` | All | `0.05 mm` |
| **Top Cover to Rotor Ring** | `TOP_COVER` | `ROTOR_RING` | `Friction (Type24)` | All | `0.05 mm` |
| **Bottom Cover to Rotor Ring** | `BOTTOM_COVER` | `ROTOR_RING` | `Friction (Type24)` | All | `0.05 mm` |

*(Note: Because we updated `mesh_races.py` earlier today, the bearings are explicitly split into `BEARING_TOP_OUTER` and `BEARING_TOP_INNER` in SimLab, making these exact contacts possible!)*

## UI Design & Workflow
1. **Contacts Tab**: A table showing the suggested contacts above. 
2. **Side-Panel Options**: If you click a row, a panel slides out allowing you to override the **Contact Type** (e.g. switch to Tied/Type2), **Solver**, **Friction Coefficient**, and **Tolerance** for that specific pair.
3. **Execution**: Clicking "Create" pulls those values, sends them over the TCP API bridge, and injects them into the `DefineManualContact` macro UUID.

## User Review Required
Please review the table of **Auto-Suggested Contact Pairs**. 
- Do these Master/Slave pairings align with your physics model?
- Do you want any default Contact Types changed to `Tied (Type 2)` instead of `Friction (Type24)`? (For instance, is the Rotor Ring glued/screwed to the Covers?)
