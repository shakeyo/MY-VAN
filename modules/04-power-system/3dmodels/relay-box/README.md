# DIN 导轨继电器盒 (Relay enclosure for a 77 × 67 mm relay)

Parameterised OpenSCAD model of a 3D-printable enclosure for a 77 × 67 mm
relay that mounts on a **TS35 (35 × 7.5) DIN rail**.

The visual language follows your `米家四路模块盒.3mf`: 3 mm walls, a 2 mm
bottom flange, a sliding lid that sits on a ledge, four lid screws and a
ribbed underside.

---

## Files

| File | Purpose |
|---|---|
| `step/relay_box_body.step` | **Editable B-rep solid** — box body |
| `step/relay_box_lid.step` | **Editable B-rep solid** — lid |
| `step/relay_box_assembly.step` | Both parts, exploded (import as an assembly) |
| `relay_box_step.py` | CadQuery source that generates the STEP files |
| `relay_box.scad` | Equivalent parametric OpenSCAD model |
| `relay_box.3mf` | Print-ready project: box + lid already on one plate |
| `stl/relay_box_body.stl` | Box body, bed-ready |
| `stl/relay_box_lid.stl` | Lid, bed-ready |
| `stl_from_step/*.stl` | Same parts meshed from the STEP solids |
| `build.py` | Rebuilds the OpenSCAD STLs and the 3MF |
| `verify_all.py` / `verify_step.py` | Acceptance checks on both pipelines |
| `renders/` | Preview images |

## Editing the STEP files

`step/*.step` are **true solids (AP214 B-rep)** — not meshes — so every
face, fillet, hole and boss is a real feature you can select and change.

| Tool | How to use |
|---|---|
| **FreeCAD** | `File → Open` the `.step`; the body imports as an editable Body with a full feature tree of faces |
| **Fusion 360 / Inventor / Solid Edge** | `Insert → Insert Mesh` is for STL; use `File → Open` or `Insert → Insert CAD` for STEP — then `Convert to Base Feature` if you want native sketch history |
| **SolidWorks** | `File → Open`, pick `.step`, then `Insert → Features → Imported` |
| **Onshape** | `Import` the STEP, then right-click → `Derive` to edit |
| **Rhino / Blender / 3ds Max** | Import directly |

To change a dimension, edit the **PARAMETERS block** at the top of
`relay_box_step.py` and re-run:

```bash
python3 relay_box_step.py     # needs cadquery (see below)
```

That regenerates all three STEP files (and matching STLs) with the new
numbers — everything downstream is derived from those constants.

One-time setup for the Python/CadQuery pipeline (already installed in
`.venv-cad/` here):

```bash
python3 -m venv .venv-cad
.venv-cad/bin/pip install cadquery
.venv-cad/bin/python relay_box_step.py
.venv-cad/bin/python verify_step.py
```

---

## Dimensions (as built)

```
outer          85.0 × 75.0 × 50.0 mm   (+3 mm DIN rib underneath)
cavity         79.0 × 69.0 × 41.0 mm   (relay 77 × 67 with 1 mm clearance)
lid            82.5 × 72.5 × 2.5 mm    (+1 mm stiffening rib)
walls / floor  3.0 mm / 2.0 mm
relay screws   72 × 62 mm pattern, Ø3.2 (M3), in four corner tabs
cable exits    44 × 24 mm window in both long walls
vents          2 rows × 6, Ø3.2 above each window
DIN rail       TS35, 35 mm wide, 7.5 mm tall, snap-on tongue + lips
```

Material: about **50 cm³** for the body and **20 cm³** for the lid, so roughly
60–90 g of PLA at typical print settings.

---

## Printing

1. Open `relay_box.3mf` (BambuStudio / OrcaSlicer) — both parts are already
   placed on the plate, flat side down.
   Otherwise import the two STLs from `stl/`.
2. **Body:** print as delivered, no supports. The DIN tongue points down into
   the bed, the cable windows print as bridges.
3. **Lid:** print flat, no supports.
4. Suggested: 0.2 mm layers, 3 perimeters, 4 top/bottom layers, 20–30 %
   infill. For anything mains-related use PETG or ABS/ASA rather than PLA —
   the relay dissipates heat and PLA creeps.

## Assembly

1. Screw the relay to the floor of the body with four M3 screws through the
   corner tabs (72 × 62 pattern). Use M3 × 8–10 self-tapping screws, or M3
   machine screws with a nut if the relay has through-holes.
2. Bring the wires out through the 44 × 24 mm side windows.
3. Put the lid on and fix it with four M3 × 6–8 screws into the corner
   ledges (blind bores, 4 mm of bite).
4. Snap the box onto the DIN rail: engage the tongue on one lip, then press
   the other side down until it clicks.

## Mounting on the rail

The underside has a tongue that drops into the rail opening and two hooks
that reach **under** the lips, so the box cannot be lifted straight off — it
slides off along the rail. Clearances are 0.4 mm for FDM tolerance.

---

## Customising

Every dimension is a named parameter at the top of `relay_box.scad`:

* `relay_w`, `relay_d`, `relay_h`, `clear` — payload size.
* `hole_dx`, `hole_dy`, `hole_d`, `tab_w`, `tab_h` — relay screw pattern.
  Set `relay_fix = false` for a plain flat floor.
* `side_win_w/h/z`, `vent*` — cable exits and ventilation.
* `wall`, `floor_t`, `lid_t`, `fit` — shell.
* `rail_w`, `rail_h`, `rail_lip`, `rail_clear` — rail profile.

Render a part with the `part` parameter:

```
openscad -o out.stl -D 'part=0' relay_box.scad   # box
openscad -o out.stl -D 'part=1' relay_box.scad   # lid
openscad -o view.png -D 'part=3' relay_box.scad  # box on a rail (preview)
```

Or open it in the OpenSCAD GUI and use the customiser panel.

## Regenerating the outputs

```
python3 build.py        # renders both STLs + relay_box.3mf, verifies manifold
python3 verify_all.py   # acceptance checks
```

> Note: this build of OpenSCAD (2026.09) evaluates the literal expression
> `79+6+4` incorrectly, so the model avoids that exact constant form and all
> key dimensions are rechecked geometrically by `verify_all.py` instead of
> being trusted from the echo output.
