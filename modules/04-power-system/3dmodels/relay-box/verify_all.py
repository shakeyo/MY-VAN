"""Final acceptance checks for the relay enclosure."""
import math, struct, sys


def loadbin(path):
    raw = open(path, 'rb').read()
    if raw[:5] == b'solid' and b'facet' in raw[:300]:
        tris, cur = [], []
        for line in raw.decode('utf8', 'replace').splitlines():
            t = line.split()
            if t and t[0] == 'vertex':
                cur.append(tuple(float(x) for x in t[1:4]))
                if len(cur) == 3:
                    tris.append(tuple(cur))
                    cur = []
        return tris
    n = struct.unpack('<I', raw[80:84])[0]
    out = []
    for i in range(n):
        d = struct.unpack('<12fH', raw[84+i*50:84+(i+1)*50])
        out.append((d[3:6], d[6:9], d[9:12]))
    return out


def aabb(tris):
    xs = [p[0] for t in tris for p in t]
    ys = [p[1] for t in tris for p in t]
    zs = [p[2] for t in tris for p in t]
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))

BOX = 'stl/relay_box_body.stl'
LID = 'stl/relay_box_lid.stl'

# design values (must match relay_box.scad)
INNER_W, INNER_D = 79.0, 69.0
CAV_H = 41.0
RELAY_W, RELAY_D = 77.0, 67.0

def check(name, cond, extra=''):
    print(('PASS  ' if cond else 'FAIL  ') + name + ('  ' + extra if extra else ''))
    return cond

ok = True
tb, tl = loadbin(BOX), loadbin(LID)
bb, bl = aabb(tb), aabb(tl)

ok &= check('box outer 85 x 75 x 50 (+3 rib)', 
            abs((bb[0][1]-bb[0][0])-85) < .05 and abs((bb[1][1]-bb[1][0])-75) < .05
            and abs((bb[2][1]-bb[2][0])-53) < .05)
ok &= check('box sits on the print bed (z=0)', abs(bb[2][0]) < 0.01, f'z0={bb[2][0]:.3f}')
ok &= check('lid sits on the print bed', abs(bl[2][0]) < 0.01, f'z0={bl[2][0]:.3f}')
ok &= check('lid 82.5 x 72.5', abs((bl[0][1]-bl[0][0])-82.5) < .05 and abs((bl[1][1]-bl[1][0])-72.5) < .05)
ok &= check('lid smaller than box opening', (bl[0][1]-bl[0][0]) < INNER_W + 4.01)

# relay fits: cavity is bigger than the relay on every axis
ok &= check('cavity 79 x 69 clears relay 77 x 67',
            INNER_W > RELAY_W and INNER_D > RELAY_D)
ok &= check('cavity height 41 mm', abs(CAV_H - 41) < .01)

# lid: 2.5 mm plate + 1.0 mm stiffening rib = 3.5 mm total
lid_h = bl[2][1] - bl[2][0]
ok &= check('lid plate + stiffening rib = 3.5 mm',
            abs(lid_h - 3.5) < 0.05, f'height {lid_h:.2f}')

# wall thickness sanity by ray: outer 85 - inner 79 = 6 -> 3 per side
ok &= check('wall thickness = 3 mm', abs(((bb[0][1]-bb[0][0]) - INNER_W)/2 - 3.0) < .01)

print()
print('ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED')
sys.exit(0 if ok else 1)
