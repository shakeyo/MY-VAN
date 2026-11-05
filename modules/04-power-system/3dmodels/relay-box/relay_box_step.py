#!/usr/bin/env python3
"""
DIN-rail relay enclosure - editable B-rep model (CadQuery / OCC kernel).

Produces true STEP (AP214) solids that can be opened and edited in
FreeCAD, Fusion 360, SolidWorks, Onshape, Inventor, Solid Edge, Rhino...

The geometry matches relay_box.scad one-to-one; change the PARAMETERS
block below and re-run to regenerate everything.

    python3 relay_box_step.py

Outputs (into ./step/):
    relay_box_body.step   box body
    relay_box_lid.step    lid
    relay_box_assembly.step  both parts, exploded and positioned
"""
import math
import os

import cadquery as cq

# =====================================================================
# PARAMETERS  (all mm)
# =====================================================================

# ---- payload: relay ----
RELAY_W = 76.0     # along the DIN rail  (X)   <- 67x76 module: 76 is the long side
RELAY_D = 67.0     # across the rail      (Y)
RELAY_H = 30.0     # overall height incl. terminals (measured 20-30; 30 = max)
CLEAR   = 1.0      # clearance relay -> wall

# ---- relay fixing ----
RELAY_FIX = True
HOLE_DX   = 72.0   # screw pitch X
HOLE_DY   = 62.0   # screw pitch Y
HOLE_D    = 3.2    # M3
TAB_W     = 12.0   # corner tab diameter
TAB_H     = 4.0    # corner tab height

# ---- shell ----
WALL      = 3.0
FLOOR_T   = 2.0
LID_T     = 2.5
FIT       = 0.25   # lid/wall lateral clearance (snap fit)
TOP_WALL  = 2.5
FLANGE    = 2.0
R_OUT     = 4.0

# ---- cable exits ----
SIDE_WIN_W = 44.0
SIDE_WIN_H = 16.0   # shortened to match the lower 30mm relay
SIDE_WIN_Z = 4.0
END_HOLE_D = 0.0
END_HOLE_Z = 15.0

# ---- ventilation ----
VENT      = True
VENT_D    = 3.2
VENT_COLS = 6
VENT_PITCH = 7.0
VENT_GAP  = 4.0

# ---- DIN rail TS35 (EN 50022) ----
RAIL_W     = 35.0
RAIL_H     = 7.5
RAIL_LIP   = 6.2
RAIL_CLEAR = 0.4
RAIL_OPEN_W = 24.0

# ---- underside ----
RIB_INSET = 1.5
RIB_W     = 4.0
RIB_DROP  = 3.0

# ---- snap-fit clips (lid -> body, no screws) ----
# A cantilever arm hangs from the lid underside (against the inner wall
# face) and ends in an outward hook; the body wall has a shallow catch
# pocket near the same height. Pressing the lid down bends the arm inward
# until the hook rides over the pocket's top edge, then it snaps outward
# and locks. Lower/higher values of CLIP_INTERF tune the tightness.
CLIP_INTERF  = 0.4    # extra hook overlap (tightness); 0.35-0.45 typical
CLIP_W       = 8.0    # arm width (along the wall)
CLIP_T       = 1.8    # arm thickness (the flexing dimension)
CLIP_ARM_L   = 12.0   # arm free length from the lid underside (flex span)
CLIP_HOOK_D  = 1.5    # hook protrusion depth (normal to wall, into pocket)
CLIP_HOOK_H  = 2.0    # hook height (vertical, catches the pocket top edge)
CLIP_CLR     = 0.25   # clearance hook <-> pocket (all around)
CLIP_OFF     = 20.0   # clip centre offset from the wall centreline
CLIP_POCKET_D = 1.8   # pocket depth into the wall (kept < wall thickness)

# =====================================================================
# derived
# =====================================================================
INNER_W = RELAY_W + 2 * CLEAR          # 78
INNER_D = RELAY_D + 2 * CLEAR          # 69
OUT_W = INNER_W + 2 * WALL             # 84
OUT_D = INNER_D + 2 * WALL             # 75
OUT_H = RELAY_H + TOP_WALL + LID_T     # 50

TOP_Z = OUT_H - LID_T                  # wall top (lid sits here) = 47.5
CAV_H = TOP_Z - FLOOR_T                # cavity height = 45.5

R_IN = R_OUT - WALL                    # 1.0

# lid now oversize: sits ON the walls, caps the whole box (no seat pocket)
LID_W = OUT_W
LID_D = OUT_D

RIB_OUT_W = OUT_W - 2 * RIB_INSET      # 81
RIB_OUT_D = OUT_D - 2 * RIB_INSET      # 72
RIB_IN_W = RIB_OUT_W - 2 * RIB_W       # 73
RIB_IN_D = RIB_OUT_D - 2 * RIB_W       # 64

LIP_IN = RAIL_W / 2 - RAIL_LIP         # 11.3
TONGUE_W = RAIL_OPEN_W - 1.2           # 22.8
TONGUE_Y = LIP_IN + RAIL_CLEAR         # 11.7

# ---- snap-fit clip derived ----
CLIP_WIN_W = CLIP_W + 2 * CLIP_CLR        # pocket width along the wall
CLIP_POCKET_Z0 = TOP_Z - CLIP_ARM_L       # pocket top edge (hook catches here)
CLIP_POCKET_H  = CLIP_HOOK_H + 2 * CLIP_CLR  # pocket height


# =====================================================================
# helpers
# =====================================================================
def rounded_solid(w, d, h, r, z0=0.0):
    """Vertical prism with rounded corners (fillet on the vertical edges)."""
    wp = cq.Workplane("XY").rect(w, d).extrude(h)
    if r > 0.01:
        wp = wp.edges("|Z").fillet(r)
    return wp.translate((0, 0, z0))


def rounded_ring_z(w_out, d_out, r_out, w_in, d_in, r_in, z0, h):
    """Flat ring (outer rounded rect minus inner rounded rect)."""
    outer = rounded_solid(w_out, d_out, h, r_out, z0)
    # extend the inner cut beyond the ring so the boolean is robust
    inner = rounded_solid(w_in, d_in, h + 2, r_in, z0 - 1)
    return outer.cut(inner)


# =====================================================================
# box body
# =====================================================================
def make_body():
    # ---- additive ----
    flange = rounded_solid(OUT_W, OUT_D, FLANGE, R_OUT)
    walls = rounded_solid(OUT_W, OUT_D, TOP_Z, R_OUT)
    body = flange.union(walls)

    # DIN rail retaining tongue underneath
    tongue = (
        cq.Workplane("XY")
        .box(TONGUE_W, 2 * TONGUE_Y, RIB_DROP + 0.05)
        .translate((0, 0, -RIB_DROP + (RIB_DROP + 0.05) / 2))
    )
    for sy in (-1, 1):
        hook = (
            cq.Workplane("XY")
            .box(TONGUE_W, 1.5, RIB_DROP + 0.05)
            .translate(
                (
                    0,
                    sy * (TONGUE_Y + 0.75) if sy > 0 else -(TONGUE_Y + 0.75),
                    -RIB_DROP + (RIB_DROP + 0.05) / 2,
                )
            )
        )
        tongue = tongue.union(hook)
    body = body.union(tongue)

    # rib loop underneath, open across the rail channel
    rib_loop = rounded_ring_z(
        RIB_OUT_W, RIB_OUT_D, 1.0, RIB_IN_W, RIB_IN_D, 0.5,
        -RIB_DROP, RIB_DROP,
    )
    channel_cut = (
        cq.Workplane("XY")
        .box(RIB_OUT_W + 4, 2 * TONGUE_Y, RIB_DROP + 2)
        .translate((0, 0, -RIB_DROP - 1 + (RIB_DROP + 2) / 2))
    )
    rib_loop = rib_loop.cut(channel_cut)
    body = body.union(rib_loop)

    # ---- subtractive ----
    # cavity
    cavity = rounded_solid(INNER_W, INNER_D, CAV_H + 0.05, R_IN, FLOOR_T)
    body = body.cut(cavity)

    # relay corner tabs: added AFTER the cavity cut so they survive;
    # they hug the inner walls and stay inside the cavity envelope.
    if RELAY_FIX:
        tabs = None
        for sx in (-1, 1):
            for sy in (-1, 1):
                tab = (
                    cq.Workplane("XY")
                    .center(sx * HOLE_DX / 2, sy * HOLE_DY / 2)
                    .circle(TAB_W / 2)
                    .extrude(TAB_H)
                    .translate((0, 0, FLOOR_T))
                )
                tabs = tab if tabs is None else tabs.union(tab)
        envelope = rounded_solid(INNER_W, INNER_D, TAB_H + 1, R_IN, FLOOR_T)
        body = body.union(tabs.intersect(envelope))

    # relay screw holes through the corner tabs
    if RELAY_FIX:
        for sx in (-1, 1):
            for sy in (-1, 1):
                hole = (
                    cq.Workplane("XY")
                    .center(sx * HOLE_DX / 2, sy * HOLE_DY / 2)
                    .circle(HOLE_D / 2)
                    .extrude(TAB_H + 0.2)
                    .translate((0, 0, FLOOR_T))
                )
                body = body.cut(hole)

    # blind lid-screw bores removed -> lid is now snap-fit (no screws)

    # side cable windows
    if SIDE_WIN_W > 0:
        for sy in (-1, 1):
            win = (
                cq.Workplane("XY")
                .box(SIDE_WIN_W, WALL + FLANGE + 6, SIDE_WIN_H)
                .translate(
                    (0, sy * OUT_D / 2,
                     FLOOR_T + SIDE_WIN_Z + SIDE_WIN_H / 2)
                )
            )
            body = body.cut(win)

    # ventilation holes above each side window
    if VENT:
        for sy in (-1, 1):
            for r in range(2):
                for c in range(VENT_COLS):
                    x = (c - (VENT_COLS - 1) / 2.0) * VENT_PITCH
                    z = (FLOOR_T + SIDE_WIN_Z + SIDE_WIN_H + VENT_GAP
                         + r * VENT_PITCH)
                    hole = (
                        cq.Workplane("XZ")
                        .center(x, z)
                        .circle(VENT_D / 2)
                        .extrude(WALL + 2)
                        .translate((0, sy * OUT_D / 2, 0))
                    )
                    # extrude dir on XZ workplane is -Y, so shift for the -Y wall
                    body = body.cut(hole)

    # round end holes (through the short X walls)
    if END_HOLE_D > 0:
        for sx in (-1, 1):
            hole = (
                cq.Workplane("YZ")
                .center(0, END_HOLE_Z)
                .circle(END_HOLE_D / 2)
                .extrude(WALL + 4)
                .translate(((WALL + 4) / 2 * (1 if sx > 0 else -1) * -1
                            if sx < 0 else -OUT_W / 2, 0, 0))
            )
            hole = (
                cq.Workplane("YZ")
                .center(0, END_HOLE_Z)
                .circle(END_HOLE_D / 2)
                .extrude(WALL + 4)
                .translate((sx * OUT_W / 2 - (WALL + 4) / 2, 0, 0))
            )
            body = body.cut(hole)

    # ---- snap-fit catch pockets on the inner faces of the four walls ----
    # A shallow pocket near the wall bottom; the lid's spring arm hangs
    # inside the cavity and its hook snaps outward into it. Depth keeps
    # wall thickness outside, so the outer face stays closed.
    pz = CLIP_POCKET_Z0 - CLIP_POCKET_H / 2   # pocket vertical centre
    for off in (CLIP_OFF, -CLIP_OFF):
        # long walls (normal +-Y): pocket runs along X, cuts inward along Y
        for sy in (-1, 1):
            pocket = (
                cq.Workplane("XY")
                .box(CLIP_WIN_W, CLIP_POCKET_D, CLIP_POCKET_H)
                .translate((off, sy * (INNER_D / 2 + CLIP_POCKET_D / 2), pz))
            )
            body = body.cut(pocket)
        # short walls (normal +-X): pocket runs along Y, cuts inward along X
        for sx in (-1, 1):
            pocket = (
                cq.Workplane("XY")
                .box(CLIP_POCKET_D, CLIP_WIN_W, CLIP_POCKET_H)
                .translate((sx * (INNER_W / 2 + CLIP_POCKET_D / 2), off, pz))
            )
            body = body.cut(pocket)

    return body


# =====================================================================
# lid
# =====================================================================
def make_lid():
    # oversize cap plate: sits flat on TOP_Z and covers the whole box
    plate = rounded_solid(LID_W, LID_D, LID_T, R_OUT)
    lid = plate

    # ---- snap-fit spring arms (two per wall) ----
    # Each arm hangs from the lid underside against the inner wall face and
    # ends in an outward hook. Pressing the lid down bends the arm inward
    # until the hook rides over the pocket's top edge, then it snaps back
    # outward and locks. Arm local z: plate underside = 0, down = negative.
    OVERLAP = LID_T                    # arm top buried into the plate to fuse
    arm_len = CLIP_ARM_L + CLIP_HOOK_H + OVERLAP   # arm spans down past the hook
    arm_z0 = OVERLAP                              # arm top (inside plate)
    arm_z1 = -CLIP_ARM_L - CLIP_HOOK_H            # arm bottom (hook base)
    arm_center_z = (arm_z0 + arm_z1) / 2
    # hook catches the pocket's top edge; a small CLIP_INTERF tightens it,
    # so the hook's top face sits slightly above the pocket edge.
    hook_top = -CLIP_ARM_L + CLIP_INTERF
    hook_z = hook_top - CLIP_HOOK_H / 2

    for off in (CLIP_OFF, -CLIP_OFF):
        # long walls (normal +-Y): arm flexes in Y, hook points outward in Y
        for sy in (-1, 1):
            arm = (
                cq.Workplane("XY")
                .box(CLIP_W, CLIP_T, arm_len)
                .translate((off, sy * (INNER_D / 2 - CLIP_T / 2), arm_center_z))
            )
            # hook spans from just inside the arm out to the pocket depth,
            # so it overlaps the arm (fusion) and hooks the wall pocket.
            hook = (
                cq.Workplane("XY")
                .box(CLIP_W, CLIP_HOOK_D + CLIP_T, CLIP_HOOK_H)
                .translate((off,
                            sy * (INNER_D / 2 + (CLIP_HOOK_D - CLIP_T) / 2),
                            hook_z))
            )
            lid = lid.union(arm).union(hook)

        # short walls (normal +-X): arm flexes in X, hook points outward in X
        for sx in (-1, 1):
            arm = (
                cq.Workplane("XY")
                .box(CLIP_T, CLIP_W, arm_len)
                .translate((sx * (INNER_W / 2 - CLIP_T / 2), off, arm_center_z))
            )
            hook = (
                cq.Workplane("XY")
                .box(CLIP_HOOK_D + CLIP_T, CLIP_W, CLIP_HOOK_H)
                .translate((sx * (INNER_W / 2 + (CLIP_HOOK_D - CLIP_T) / 2),
                            off, hook_z))
            )
            lid = lid.union(arm).union(hook)

    return lid


# =====================================================================
# output
# =====================================================================
def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "step")
    os.makedirs(out, exist_ok=True)

    body = make_body()
    lid = make_lid()

    cq.exporters.export(body, os.path.join(out, "relay_box_body.step"))
    cq.exporters.export(lid, os.path.join(out, "relay_box_lid.step"))

    # exploded assembly, lid raised above the body
    lid_up = lid.translate((0, 0, OUT_H + 60))
    asm = cq.Assembly()
    asm.add(body, name="box_body", color=cq.Color(0.15, 0.30, 0.55))
    asm.add(lid_up, name="lid", color=cq.Color(0.25, 0.45, 0.75))
    asm.save(os.path.join(out, "relay_box_assembly.step"))

    # STL copies for slicers, generated from the same solids
    # (kept separate from the OpenSCAD outputs so the two never clobber
    #  each other)
    stl_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "stl_from_step")
    os.makedirs(stl_dir, exist_ok=True)
    # body: drop the DIN rib onto the bed (z = 0)
    body_bed = body.translate((0, 0, RIB_DROP))
    cq.exporters.export(body_bed, os.path.join(stl_dir, "relay_box_body.stl"),
                        tolerance=0.02)
    cq.exporters.export(lid, os.path.join(stl_dir, "relay_box_lid.stl"),
                        tolerance=0.02)

    bb = body.val().BoundingBox()
    lb = lid.val().BoundingBox()
    print(f"body : {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm")
    print(f"lid  : {lb.xlen:.2f} x {lb.ylen:.2f} x {lb.zlen:.2f} mm")
    print(f"solids: body={len(body.val().Solids())}, lid={len(lid.val().Solids())}")
    print(f"written to {out}")


if __name__ == "__main__":
    main()
