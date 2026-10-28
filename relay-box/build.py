#!/usr/bin/env python3
"""
Build printable outputs for the DIN-rail relay box.

Runs OpenSCAD for each part, checks the result is manifold, and packs
the two STLs into a BambuStudio-friendly 3MF.

Usage:  python3 build.py
"""
import os
import struct
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCAD = os.path.join(HERE, 'relay_box.scad')
STL_DIR = os.path.join(HERE, 'stl')
PARTS = [
    # (part number, file stem, expected (x, y, z) size)
    (0, 'relay_box_body', (85.0, 75.0, 53.0)),
    (1, 'relay_box_lid', (82.5, 72.5, 3.5)),
]


def load_stl(path):
    raw = open(path, 'rb').read()
    if raw[:5] == b'solid' and b'facet' in raw[:300]:
        tris, cur = [], []
        for line in raw.decode('utf8', 'replace').splitlines():
            t = line.split()
            if t and t[0] == 'vertex':
                cur.append(tuple(float(v) for v in t[1:4]))
                if len(cur) == 3:
                    tris.append(tuple(cur))
                    cur = []
        return tris
    n = struct.unpack('<I', raw[80:84])[0]
    return [(struct.unpack('<12fH', raw[84+i*50:84+(i+1)*50])[3:12],
             struct.unpack('<12fH', raw[84+i*50:84+(i+1)*50])[6:9],
             struct.unpack('<12fH', raw[84+i*50:84+(i+1)*50])[9:12])
            for i in range(n)]


def bounds(tris):
    xs = [p[0] for t in tris for p in t]
    ys = [p[1] for t in tris for p in t]
    zs = [p[2] for t in tris for p in t]
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))


def render(part, out):
    cmd = ['openscad', '-o', out, '--export-format', 'binstl',
           '-D', f'part={part}', '-D', '$fn=96', SCAD]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f'openscad failed for part {part}\n{r.stderr}')
    log = r.stdout + r.stderr
    if 'manifold' not in log or 'NoError' not in log:
        sys.exit(f'part {part} is not a clean manifold\n{log}')


def write_3mf(path, items):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
             ' <metadata name="Application">relay box build script</metadata>',
             ' <resources>']
    for idx, (name, stl, off) in enumerate(items):
        verts, vlist, tlist = {}, [], []
        for tri in load_stl(stl):
            ids = []
            for p in tri:
                key = (round(p[0], 5), round(p[1], 5), round(p[2], 5))
                if key not in verts:
                    verts[key] = len(vlist)
                    vlist.append(key)
                ids.append(verts[key])
            tlist.append(ids)
        lines.append(f'  <object id="{idx+2}" type="model" name="{name}">')
        lines.append('   <mesh><vertices>')
        lines += [f'    <vertex x="{v[0]:.5f}" y="{v[1]:.5f}" z="{v[2]:.5f}"/>'
                  for v in vlist]
        lines.append('   </vertices><triangles>')
        lines += [f'    <triangle v1="{t[0]}" v2="{t[1]}" v3="{t[2]}"/>'
                  for t in tlist]
        lines.append('   </triangles></mesh>')
        lines.append('  </object>')
    lines.append(' </resources><build>')
    for idx, (name, stl, off) in enumerate(items):
        lines.append('  <item objectid="{}" transform="1 0 0 0 1 0 0 0 1 {} {} {}"/>'
                     .format(idx + 2, off[0], off[1], off[2]))
    lines.append(' </build></model>')
    xml = '\n'.join(lines)

    types = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
             ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
             ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
             '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            ' <Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
            '</Relationships>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', types)
        z.writestr('_rels/.rels', rels)
        z.writestr('3D/3dmodel.model', xml)


def main():
    os.makedirs(STL_DIR, exist_ok=True)
    items = []
    for part, stem, ideal in PARTS:
        out = os.path.join(STL_DIR, stem + '.stl')
        render(part, out)
        tris = load_stl(out)
        bb = bounds(tris)
        size = tuple(round(b[1] - b[0], 2) for b in bb)
        ok = all(abs(s - e) < 0.35 for s, e in zip(size, ideal))
        print(f'{stem:18s} {size[0]:6.2f} x {size[1]:6.2f} x {size[2]:6.2f} mm '
              f'z[{bb[2][0]:6.2f},{bb[2][1]:6.2f}]  {"OK" if ok else "CHECK"}')
        items.append((stem.replace('relay_box_', ''), out, (0, 0, 0)))

    # lay the parts out side by side on one plate
    items[1] = (items[1][0], items[1][1], (130, 0, 0))
    write_3mf(os.path.join(HERE, 'relay_box.3mf'), items)
    print('wrote relay_box.3mf')


if __name__ == '__main__':
    main()
