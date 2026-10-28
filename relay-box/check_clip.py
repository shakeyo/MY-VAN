#!/usr/bin/env python3
"""
Verify snap-fit geometry between the lid hooks and body catch pockets.

Imports the real PARAMETERS from relay_box_step.py so the check always
matches whatever dimensions the model was last generated with.

Assembles the lid onto the body (lid underside z=0 -> TOP_Z) and reports
the hook/pocket interference (intended = CLIP_INTERF overlap per hook,
unintended = anything else that would prevent closing).
"""
import os
import sys

import cadquery as cq
from cadquery import exporters

# pull the true constants out of the model script
import importlib.util
spec = importlib.util.spec_from_file_location(
    'rbs', os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'relay_box_step.py'))
rbs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rbs)

TOP_Z = rbs.TOP_Z
INNER_W, INNER_D = rbs.INNER_W, rbs.INNER_D
CLIP_OFF = rbs.CLIP_OFF
CLIP_INTERF = rbs.CLIP_INTERF
CLIP_HOOK_D = rbs.CLIP_HOOK_D

body = cq.importers.importStep('step/relay_box_body.step').val()
lid = cq.importers.importStep('step/relay_box_lid.step').val()

lid_as = cq.Workplane('XY').add(lid.translate((0, 0, TOP_Z)))

print('TOP_Z =', TOP_Z)
print('body solids:', len(body.Solids()))
print('lid  solids:', len(lid_as.val().Solids()))
print('body bb:', [round(v, 2) for v in (body.BoundingBox().xlen,
      body.BoundingBox().ylen, body.BoundingBox().zlen)])
print('lid  bb:', [round(v, 2) for v in (lid_as.val().BoundingBox().xlen,
      lid_as.val().BoundingBox().ylen, lid_as.val().BoundingBox().zlen)])

# Intersection of assembled parts: should be exactly 8 hook tips, each a
# CLIP_INTERF-thick sliver where the hook rides over the pocket top edge.
inter = body.intersect(lid_as.val())
sols = inter.Solids() if inter else []
vol = sum(s.Volume() for s in sols)
print('intersect solids:', len(sols), 'volume:', round(vol, 3), 'mm^3')
if sols:
    bb = inter.BoundingBox()
    print('  intersect bb:', round(bb.xlen, 2), round(bb.ylen, 2),
          round(bb.zlen, 2), 'z', round(bb.zmin, 2), round(bb.zmax, 2))

# expected: 8 hooks * (CLIP_W * CLIP_HOOK_D * CLIP_INTERF)
expect_vol = 8 * rbs.CLIP_W * CLIP_HOOK_D * CLIP_INTERF
print('expected hook interference ~', round(expect_vol, 3), 'mm^3')

# quick sanity: none of the hook tips should be buried inside solid wall
# below the pocket top (that would mean the lid cannot close).
bad = 0
for off in (CLIP_OFF, -CLIP_OFF):
    for sign in (1, -1):
        # long walls (+-Y)
        p = cq.Vector(off, sign * (INNER_D / 2 + CLIP_HOOK_D / 2),
                      TOP_Z - rbs.CLIP_ARM_L)
        if any(s.isInside(p) for s in body.Solids()) and not any(
                s.isInside(p) for s in lid_as.val().Solids()):
            bad += 1
print('hook-tip wall conflicts:', bad)
print('OK' if len(sols) == 8 and bad == 0 else 'REVIEW NEEDED')
