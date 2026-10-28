// =====================================================================
//  DIN 导轨继电器盒 / DIN-rail relay enclosure
//  Parametric OpenSCAD model, all units in mm
//
//  Payload : relay 77 x 67 mm footprint, M3 screws on a 72 x 62 pattern
//  Mount   : TS35 (35 x 7.5) DIN rail, snap-on underside
//
//  Design language taken from the user's 米家四路模块盒.3mf:
//    3 mm walls, 2 mm floor, 2 mm bottom flange, sliding lid on a seat
//    ledge, four lid screws, ribbed underside.
//
//  Rendering:  part = 0 box / 1 lid / 2 assembly / 3 box on a DIN rail
// =====================================================================

/* [Part] */
part    = 0;   // [0:box, 1:lid, 2:assembly, 3:box on rail]
render  = 1;   // 1 = draw the selected part, 0 = modules only
explode = 0;   // lid lift for the preview [0:150]

/* [Relay] */
relay_w = 77;    // along the rail
relay_d = 67;    // across the rail
relay_h = 45;    // overall height incl. terminals
clear   = 1.0;   // relay -> wall clearance

/* [Relay fixing] */
relay_fix  = true;  // mount the relay with 4 screws
hole_dx = 72;    // screw hole pitch, X
hole_dy = 62;    // screw hole pitch, Y
hole_d  = 3.2;   // M3 clearance hole
hole_depth = 2.0; // how far the pilot hole enters the tab
tab_w   = 12.0;  // corner tab width
tab_t   = 4.0;   // corner tab thickness (sticks out of the inner wall)
tab_h   = 4.0;   // corner tab height
use_inserts = false;
insert_d = 5.0;

/* [Shell] */
wall     = 3.0;
floor_t  = 2.0;
lid_t    = 2.5;
fit      = 0.25;  // lid clearance
post_l   = 2.0;   // seat step width
top_wall = 2.5;   // wall above the seat
seat_t   = 4.5;   // seat ledge height

/* [Cable exits] */
side_win_w = 44;  // window in both long walls
side_win_h = 24;
side_win_z = 4;   // above the inner floor
end_hole_d = 0;   // round hole in the short walls (0 = off)
end_hole_z = 20;

/* [Ventilation] */
vent       = true;
vent_d     = 3.2;
vent_cols  = 6;
vent_pitch = 7;
vent_gap   = 4;

/* [DIN rail TS35, EN 50022] */
rail_w     = 35.0;  // width
rail_h     = 7.5;   // height above the mounting surface
rail_lip   = 6.2;   // inward lip depth
rail_clear = 0.4;   // sliding clearance

/* [Underside] */
rib_inset = 1.5;    // rib inset from the outer wall
rib_w     = 4.0;    // rib width
rib_drop  = 3.0;    // rib protrusion below the outside floor

$fn = 64;

// ---------------------------------------------------------------------
// derived
// ---------------------------------------------------------------------
inner_w = relay_w + 2*clear;            // 79
inner_d = relay_d + 2*clear;            // 69

flange = 2.0;
out_w  = inner_w + 2*wall;              // 85
out_d  = inner_d + 2*wall;              // 75
out_h  = relay_h + top_wall + lid_t;    // 50

seat_z = out_h - lid_t - seat_t;        // ledge top z
cav_h  = seat_z - floor_t;              // cavity height

r_out  = 4.0;
r_in   = r_out - wall;                  // 1.0

seat_in_w = inner_w + 2*post_l - 2*fit; // 83
seat_in_d = inner_d + 2*post_l - 2*fit; // 73
seat_in_r = r_in + post_l;              // 3

lid_w = seat_in_w;
lid_d = seat_in_d;

// rib loop on the underside
rib_out_w = out_w - 2*rib_inset;        // 82
rib_out_d = out_d - 2*rib_inset;        // 72
rib_in_w  = rib_out_w - 2*rib_w;        // 74
rib_in_d  = rib_out_d - 2*rib_w;        // 64

// lid screws: blind bores in the seat corner landings
screw_bite = 4.0;
screw_x = seat_in_w*0.5 - 4.0;
screw_y = seat_in_d*0.5 - 4.0;

// DIN rail hook geometry. z = 0 is the outside floor, the rail's
// cross-section sits below it when mounted.
lip_in   = rail_w*0.5 - rail_lip;      // 11.3  inner face of the lip
open_w   = 24.0;                       // rail opening width
tongue_w = open_w - 1.2;               // 22.8
tongue_y = lip_in + rail_clear;        // 11.7

module rrect(w, d, r)
{
    if (r < 0.05) square([w, d], center = true);
    else hull()
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx*(w*0.5 - r), sy*(d*0.5 - r)]) circle(r = r);
}

module rbox(w, d, h, r)
{
    linear_extrude(height = h) rrect(w, d, r);
}

// ---------------------------------------------------------------------
// TS35 rail, drawn only for fit checking. Origin = rail top face.
// ---------------------------------------------------------------------
module din_rail(l = 220)
{
    // TS35 rail built from prisms. Runs along X; the top face is z = 0,
    // the bottom z = -rail_h (+-17.5 outer faces).
    //   web   : the full top plate, 4.5 .. 7.5 below the top face
    //   sides : outer walls from the bottom up
    //   lips  : folded inward to +-lip_in, from the bottom up to 4.5 below top
    color("silver")
    {
        // top plate (full width)
        translate([-l*0.5, -rail_w*0.5, -rail_h + 4.5])
            cube([l, rail_w, 3.0]);
        // outer side walls below the top plate
        for (sy = [-1, 1])
            translate([-l*0.5,
                       sy > 0 ? rail_w*0.5 - 0.6 : -rail_w*0.5,
                       -rail_h])
                cube([l, 0.6, 4.5]);
        // folded lips (inward)
        for (sy = [-1, 1])
            translate([-l*0.5,
                       sy > 0 ? lip_in : -lip_in,
                       -rail_h])
                cube([l, lip_in - (rail_w*0.5 - 0.6), 4.5]);
    }
}

// ---------------------------------------------------------------------
// DIN mounting on the underside. All geometry is below z = 0.
// The tongue drops into the rail opening; two hooks reach outward and
// sit UNDER the lips, so the box can only be slid off along the rail.
// ---------------------------------------------------------------------
module din_mount()
{
    // tongue through the rail opening
    translate([-tongue_w*0.5, -tongue_y, -rib_drop])
        cube([tongue_w, 2*tongue_y, rib_drop + 0.05]);

    // hooks that tuck under the lips
    for (sy = [-1, 1])
        translate([-tongue_w*0.5,
                   sy > 0 ? tongue_y - 0.01 : -tongue_y - 1.5,
                   -rib_drop])
            cube([tongue_w, 1.5, rib_drop + 0.05]);

    // rib loop, open across the rail channel
    translate([0, 0, -rib_drop])
        difference()
        {
            linear_extrude(height = rib_drop)
                rrect(rib_out_w, rib_out_d, 1.0);
            translate([0, 0, -1])
                linear_extrude(height = rib_drop + 2)
                    rrect(rib_in_w, rib_in_d, 0.5);
            translate([0, 0, -1])
                linear_extrude(height = rib_drop + 2)
                    square([rib_out_w + 4, 2*tongue_y], center = true);
        }
}

// ---------------------------------------------------------------------
// BOX BODY
// ---------------------------------------------------------------------
module box_body()
{
    difference()
    {
        union()
        {
            rbox(out_w, out_d, flange, r_out);          // bottom flange
            rbox(out_w, out_d, out_h, r_out);           // walls
            // relay corner tabs: small pads that grow out of the inner
            // walls at the 72 x 62 screw pattern, so the floor stays flat
            // and the relay keeps its full 77 x 67 footprint.
            if (relay_fix)
                for (sx = [-1, 1], sy = [-1, 1])
                    translate([sx*hole_dx*0.5, sy*hole_dy*0.5, floor_t])
                        intersection()
                        {
                            cylinder(d = tab_w, h = tab_h, $fn = 40);
                            translate([0, 0, -0.01])
                                linear_extrude(height = tab_h + 1)
                                    rrect(inner_w, inner_d, r_in);
                        }
            din_mount();                                // rail interface
            // seat ledge ring
            translate([0, 0, seat_z - seat_t])
                difference()
                {
                    linear_extrude(height = seat_t + 0.05)
                        rrect(out_w, out_d, r_out);
                    translate([0, 0, -1])
                        linear_extrude(height = seat_t + 2)
                            rrect(seat_in_w, seat_in_d, seat_in_r);
                }
        }

        // cavity (the mounting pillars stay solid inside it)
        translate([0, 0, floor_t])
            linear_extrude(height = cav_h + 0.05)
                difference()
                {
                    rrect(inner_w, inner_d, r_in);
                    if (relay_fix)
                        for (sx = [-1, 1], sy = [-1, 1])
                            translate([sx*hole_dx*0.5, sy*hole_dy*0.5])
                                circle(d = tab_w, $fn = 40);
                }

        // seat pocket
        translate([0, 0, seat_z])
            linear_extrude(height = out_h - seat_z + 1)
                rrect(seat_in_w, seat_in_d, seat_in_r);

        // relay mounting holes (through the corner tabs)
        if (relay_fix)
            for (sx = [-1, 1], sy = [-1, 1])
                translate([sx*hole_dx*0.5, sy*hole_dy*0.5, floor_t])
                    cylinder(d = hole_d, h = tab_h + 0.2, $fn = 32);

        // blind lid-screw bores in the ledge corners
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx*screw_x, sy*screw_y, seat_z - screw_bite])
                cylinder(d = use_inserts ? insert_d : hole_d,
                         h = screw_bite + seat_t + 1, $fn = 32);

        // side cable windows
        if (side_win_w > 0)
            for (sy = [-1, 1])
                translate([0, sy*out_d*0.5,
                           floor_t + side_win_z + side_win_h*0.5])
                    cube([side_win_w, wall + flange + 6, side_win_h],
                         center = true);

        // round end holes
        if (end_hole_d > 0)
            for (sx = [-1, 1])
                translate([sx*out_w*0.5, 0, end_hole_z])
                    rotate([0, 90, 0])
                        cylinder(d = end_hole_d, h = wall + 4, center = true);

        // vents above the windows
        if (vent)
            for (sy = [-1, 1], r = [0 : 1], c = [0 : vent_cols - 1])
                translate([(c - (vent_cols - 1)*0.5)*vent_pitch,
                           sy*out_d*0.5,
                           floor_t + side_win_z + side_win_h + vent_gap
                           + r*vent_pitch])
                    rotate([90, 0, 0])
                        cylinder(d = vent_d, h = wall + 2, center = true);
    }
}

// ---------------------------------------------------------------------
// LID
// ---------------------------------------------------------------------
module lid()
{
    // plate underside at z = 0, rib on top
    {
        linear_extrude(height = lid_t)
            rrect(lid_w, lid_d, seat_in_r);

        // stiffening rib
        translate([0, 0, lid_t])
            linear_extrude(height = 1.0)
                offset(delta = -5) rrect(lid_w, lid_d, seat_in_r);

        // screw holes (through the plate, clear of the rib)
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx*screw_x, sy*screw_y, -0.005])
                cylinder(d = hole_d + 0.6, h = 2.0);
    }
}

// ---------------------------------------------------------------------
// Set render=0 when including this file from another script so that
// only the requested modules are instantiated.
if (render == 0) {
    // no geometry: used by fit/test scripts
} else if (part == 0) translate([0, 0, rib_drop]) box_body();
else if (part == 1) lid();
else if (part == 2) {
    box_body();
    translate([0, 0, out_h + explode]) lid();
} else if (part == 3) {
    box_body();
    translate([0, 0, -rib_drop - rail_h]) din_rail();
}

echo("OUTER  X Y Z =", out_w, out_d, out_h, " (+", rib_drop, " rib under)");
echo("CAVITY =", inner_w, "x", inner_d, "x", cav_h);
echo("LID    =", lid_w, "x", lid_d, "x", lid_t);
echo("WINDOW =", side_win_w, "x", side_win_h);
echo("SCREWS =", hole_dx, "x", hole_dy, "dia", hole_d);
