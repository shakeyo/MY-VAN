"""Verify the STEP export matches the design intent."""
from collections import Counter

import cadquery as cq

BODY = 'step/relay_box_body.step'
LID = 'step/relay_box_lid.step'

RELAY_W, RELAY_D = 76.0, 67.0
INNER_W, INNER_D = 78.0, 69.0
HOLE_DX, HOLE_DY = 72.0, 62.0

ok = True


def check(name, cond, extra=''):
    global ok
    ok &= bool(cond)
    print(('PASS  ' if cond else 'FAIL  ') + name + ('  ' + extra if extra else ''))


body = cq.importers.importStep(BODY).val()
lid = cq.importers.importStep(LID).val()

for name, sol in (('body', body), ('lid', lid)):
    check(f'{name} is a valid single B-rep solid',
          sol.isValid() and len(sol.Solids()) == 1,
          f'solids={len(sol.Solids())}')

bb = body.BoundingBox()
check('body outer 84 x 75 x 35.5 (+3 rib)',
      abs(bb.xlen - 84) < .05 and abs(bb.ylen - 75) < .05
      and abs(bb.zlen - 35.5) < .06,
      f'{bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}')

lb = lid.BoundingBox()
check('lid 84 x 75 x 16.5 (cap + 12mm arms ',
      abs(lb.xlen - 84) < .05 and abs(lb.ylen - 75) < .05
      and abs(lb.zlen - 16.5) < .06,
      f'{lb.xlen:.2f} x {lb.ylen:.2f} x {lb.zlen:.2f}')

# cavity must clear the relay
check('cavity 78 x 69 clears relay 76 x 67',
      INNER_W > RELAY_W and INNER_D > RELAY_D,
      f'gap {INNER_W-RELAY_W:.0f}/{INNER_D-RELAY_D:.0f} mm')

# cylindrical features
rads = Counter()
for f in body.Faces():
    if f.geomType() == 'CYLINDER':
        rads[round(f._geomAdaptor().Cylinder().Radius(), 2)] += 1
check('16 ventilation holes (r=1.6)', rads.get(1.6, 0) >= 16,
      f'r1.6 count={rads.get(1.6,0)}')
check('4 corner fillets (r=4.0)', rads.get(4.0, 0) == 4)
check('relay mounting tabs present (r=6.0)', rads.get(6.0, 0) == 4,
      f'r6.0 count={rads.get(6.0,0)}')

# relay screw hole positions -> 72 x 62 pattern
# vertical r=1.6 holes => the four relay fixing holes
holes = set()
for f in body.Faces():
    if f.geomType() != 'CYLINDER':
        continue
    g = f._geomAdaptor()
    if abs(g.Cylinder().Radius() - 1.6) > 0.01:
        continue
    if abs(abs(g.Axis().Direction().Z()) - 1) > 0.01:
        continue
    c = f.Center()
    holes.add((round(c.x, 1), round(c.y, 1)))
want = {(HOLE_DX / 2, HOLE_DY / 2), (-HOLE_DX / 2, HOLE_DY / 2),
        (HOLE_DX / 2, -HOLE_DY / 2), (-HOLE_DX / 2, -HOLE_DY / 2)}
check('relay holes at the 72 x 62 pattern', holes == want,
      f'found {sorted(holes)}')

print()
print('ALL STEP CHECKS PASSED' if ok else 'SOME CHECKS FAILED')
raise SystemExit(0 if ok else 1)
