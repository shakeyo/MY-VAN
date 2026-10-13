#!/usr/bin/env python3
"""
平板支架 / 平板假体 —— 生成 STEP（可直接在 Shapr3D 编辑）

为什么用 CadQuery 重写而不是转 STL：
  STL 是三角网格，Shapr3D 里改不动尺寸（只能整体缩放，会同时改变内腔和壁厚）。
  CadQuery 生成的是真 BREP 实体，导出 STEP 后每个面/边都可编辑。

尺寸来源：tablet-mount.scad（小米平板4 8"：200.2 × 120.3 × 7.9）
⚠ 本文件必须与 tablet-mount.scad 保持同步（两条生成路径，改一处要改另一处）
用法：python gen_step.py            # 输出到 ./step/
"""
import os
import cadquery as cq

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "step")
os.makedirs(OUT, exist_ok=True)

# ---------- 平板尺寸 ----------
TAB_W, TAB_H, TAB_T = 200.2, 120.3, 7.9

# ---------- 托盘参数 ----------
CLEAR     = 1.0     # 单侧取放间隙
WALL_TH   = 3.0
LIP_D     = 5.0     # 托边深度
LIP_H     = 8.0     # 托边高度
CLAMP_H   = 3.0     # 压边前唇厚度（Z 向）
CLAMP_GRIP= 2.0     # 压边前唇压住平板上沿的量（Y 向）
BACK_T    = 3.0

# ---------- R 角 ----------
R_TAB     = 8.0     # 平板真机四角（估值）
R_CAVITY  = 3.0     # ⚠ 内腔圆角必须 ≤ ~4：真机 R8 + 1mm 间隙 → 圆角 >4 会与
                    #   平板四角干涉装不进去（旧版 R10 实测干涉约 6mm，已修正）
R_OUTER   = 10.0
R_FILLET  = 2.0     # 托边根部圆角
R_BASE    = 4.0     # 球头底座外角

# ---------- 底座参数 ----------
TILT      = 22.0    # 楔形倾角
BASE_T    = 6.0
QUARTER_D = 6.35    # 1/4" 螺丝通过孔
INSERT_D  = 8.2     # 1/4 热熔铜螺母嵌件孔（嵌件外径 8.4）
INSERT_H  = 8.0     # 嵌件孔深
QUARTER_H = 9.0     # 螺母座高

# ---------- 收纳挂槽（吊顶收纳用）----------
HOOK_D      = 5.0   # 挂钩直径
HOOK_OFFSET = 38.0  # 挂槽中心距托盘顶（避开 1/4 座）


def export(shape, name):
    p = os.path.join(OUT, f"{name}.step")
    cq.exporters.export(shape, p)
    bb = shape.val().BoundingBox()
    print(f"  {name+'.step':34} "
          f"{bb.xlen:6.1f} × {bb.ylen:6.1f} × {bb.zlen:5.1f} mm  "
          f"{os.path.getsize(p)/1024:6.1f} KB")
    return p


# =============================================================
# 1. 平板假体（用于打印试装）
# =============================================================
def tablet_dummy(hollow=True, finger=True):
    w, h, t = TAB_W, TAB_H, TAB_T
    if not hollow:
        s = (cq.Workplane("XY")
             .box(w, h, t)
             .edges("|Z").fillet(R_TAB))
    else:
        st = 1.6
        outer = cq.Workplane("XY").box(w, h, t).edges("|Z").fillet(R_TAB)
        inner = (cq.Workplane("XY")
                 .box(w - st*2, h - st*2, t)          # 上下贯通，留上下壳
                 .edges("|Z").fillet(max(R_TAB - st, 0.5))
                 .translate((0, 0, 0)))
        # 掏空：只留上下壳 + 四周壳
        s = outer.cut(inner)
        # 加强筋
        for i in range(3):
            y = -h/2 + h*(i+1)/(3+1)
            rib = (cq.Workplane("XY")
                   .box(w - st*2, 2.0, t - st*2)
                   .translate((0, y, 0)))
            s = s.union(rib)

    if finger:
        # 指孔（长圆孔）：上边中部
        fh = (cq.Workplane("XY")
              .slot2D(36, 22, 90)
              .extrude(t + 4)
              .translate((0, h/2 - 28, -2)))
        s = s.cut(fh)
    return s


# =============================================================
# 2. 托盘（装平板）
# =============================================================
def tray(hook_slot=False):
    """托盘：Z=0 是背板外表面，开口朝 +Z；Y=0 是底部托边下沿。

    Z 方向分层：
      0 ................. BACK_T            背板（实心，与底座连接）
      BACK_T ............ BACK_T+TAB_T      平板占据（内腔）
      BACK_T+TAB_T ...... depth             前方开口（托边/压边悬垂）
    Y 方向分层：
      0 ................. LIP_H             底部托边（承重）
      LIP_H ............. LIP_H+ih          内腔（平板）
      压边 = L 形：前唇压平板上沿 2mm + 横梁防脱出
    X 方向：以 0 居中，±ow/2
    """
    iw = TAB_W + CLEAR*2
    ih = TAB_H + CLEAR*2
    ow = iw + WALL_TH*2
    oh = LIP_H + ih + CLAMP_H + WALL_TH
    depth = TAB_T + LIP_D + BACK_T

    # 外形：X 居中、Y 从 0、Z 从 0
    s = (cq.Workplane("XY")
         .box(ow, oh, depth, centered=(True, False, False))
         .edges("|Z").fillet(R_OUTER))

    # 内腔：X 居中；Y 从 LIP_H 到 LIP_H+ih；Z 从 BACK_T 向前贯通
    # 内腔竖边 R3（≤4 防与平板 R8 干涉）；托边根部 R2 减应力
    cav = (cq.Workplane("XY")
           .box(iw, ih, depth, centered=(True, False, False))
           .edges("|Z").fillet(R_CAVITY)
           .edges("<Y and <Z").fillet(R_FILLET)
           .translate((0, LIP_H, BACK_T)))
    s = s.cut(cav)

    # 压边横梁（平板上沿 +1mm 到托盘顶，防脱出）
    bar_y = LIP_H + TAB_H + CLEAR
    s = s.union(cq.Workplane("XY")
                .box(iw, oh - bar_y, depth - BACK_T, centered=(True, False, False))
                .translate((0, bar_y, BACK_T)))
    # 压边前唇（压住平板上沿 CLAMP_GRIP）
    lip_y = LIP_H + TAB_H - CLAMP_GRIP
    s = s.union(cq.Workplane("XY")
                .box(iw, CLAMP_GRIP + CLEAR, CLAMP_H, centered=(True, False, False))
                .translate((0, lip_y, BACK_T + TAB_T)))

    # 散热孔（背板 φ4 阵列）+ 侧壁通风槽 + 走线缺口
    for r in range(4):
        for c in range(8):
            s = s.cut(cq.Workplane("XY")
                      .center(WALL_TH + 8 + c*((iw-16)/7) - ow/2,
                              LIP_H + 10 + r*((ih-20)/3))
                      .circle(2).extrude(BACK_T + 2)
                      .translate((0, 0, -1)))
    for y0 in (28, 62, 96):
        s = s.cut(cq.Workplane("XY")
                  .box(6, 3, depth - BACK_T, centered=(True, True, False))
                  .translate((ow/2 - 1.5, y0, BACK_T)))
        s = s.cut(cq.Workplane("XY")
                  .box(6, 3, depth - BACK_T, centered=(True, True, False))
                  .translate((-(ow/2 - 1.5), y0, BACK_T)))
    for sx in (-1, 1):
        s = s.cut(cq.Workplane("XY")
                  .box(6, 12, 11, centered=(True, True, False))
                  .translate((sx*(ow/2 - 1.5), 20, BACK_T)))

    # 4×M3 沉头孔（连接底座）—— 从内腔侧钻，沉头与背板内面齐平
    for dx in (-1, 1):
        for dy in (-1, 1):
            px = dx*(ow/2 - 18); py = oh/2 + dy*(oh/2 - 18)
            cone = cq.Solid.makeCone(6.2/2, 3.2/2, 1.91).translate((px, py, BACK_T - 1.9))
            cyl  = cq.Solid.makeCylinder(3.2/2, BACK_T + 1.2).translate((px, py, -1))
            s = s.cut(cone).cut(cyl)

    # 吊顶：1/4" 热熔螺母座（背面中心 φ20×10 + 嵌件孔 φ8.2×8）
    if hook_slot:
        # ⚠ cylinder 默认 Z 向居中（z∈[-h/2, h/2]），需 -5 平移到 [-10, 0]
        s = s.union(cq.Workplane("XY").cylinder(10, 10).translate((0, oh/2, -5)))
        s = s.cut(cq.Workplane("XY").circle(INSERT_D/2).extrude(INSERT_H + 0.5)
                  .translate((0, oh/2, -9.5)))
        s = s.cut(cq.Workplane("XY").circle(QUARTER_D/2).extrude(5)
                  .translate((0, oh/2, -2)))

    # 收纳挂槽（吊顶收纳用）：背板外侧加凸台 + 横向长圆槽
    if hook_slot:
        boss = (cq.Workplane("XY")
                .box(24, 18, HOOK_D + 3, centered=(True, True, False))
                .translate((0, oh - HOOK_OFFSET, -(HOOK_D + 3))))
        s = s.union(boss)
        # ⚠ "YZ" 工作平面：u→世界 Y，v→世界 Z；槽沿 X 挤出贯通
        slot = (cq.Workplane("YZ")
                .center(oh - HOOK_OFFSET, -(HOOK_D/2 + 1))
                .slot2D(12, HOOK_D + 0.4, 0)
                .extrude(34)
                .translate((-17, 0, 0)))
        s = s.cut(slot)

    return s


# =============================================================
# 3. 楔形底座（倾角由 tan(θ)=进深/高 决定）
# =============================================================
def wedge_base(bw, bh, tilt, th=5.0):
    """楔形底座：宽 bw（X）、高 bh（Z）、进深 bd=bh*tan(θ)（Y）。

    坐标约定（便于在 Shapr3D 里理解）：
      贴墙面 = X-Z 平面（Y=0，平贴柜面/顶棚）
      斜面   = 从 (Y=0, Z=bh) 到 (Y=bd, Z=0)
      沿 X 方向挤出宽度 bw（居中，与托盘坐标一致）

    ⚠ 掏空必须【等距偏移】，不能按尺寸收缩：收缩后的斜面不平行，
      上部会戳穿外斜面（旧版已踩坑，斜面上半段被掏空）。
    """
    import math
    rad = math.radians(tilt); s = math.sin(rad); c = math.cos(rad)
    bd = bh * s / c

    # 顶部截平 4mm（去刀口）
    TRUNC = 4.0
    y_t = bd * TRUNC / bh
    prof_outer = [(0, 0), (bd, 0), (y_t, bh - TRUNC), (0, bh - TRUNC)]
    # ⚠ extrude(both=True) 是每方向各挤 until 长度，总宽 = 2*until
    outer = (cq.Workplane("YZ").polyline(prof_outer + [prof_outer[0]])
             .close().extrude(bw/2, both=True))

    # 等距掏空：内三角 = 斜面/贴墙面/底面各内缩 th 的交点
    z_apex = (bd*c - th*(1+c)) / s
    y_front = (bd*c - th*(1+s)) / c
    prof_inner = [(th, th), (y_front, th), (th, z_apex)]
    inner = (cq.Workplane("YZ").polyline(prof_inner + [prof_inner[0]])
             .close().extrude((bw - th*2)/2, both=True))
    s_ = outer.cut(inner)

    # 内部竖向筋（Y-Z 板 ×3，撑斜面 + 给螺丝加肉）
    for xr in (-bw/4, 0, bw/4):
        rib = (cq.Workplane("YZ")
               .polyline([(0, 0), (bd, 0), (0, bh - TRUNC), (0, 0)])
               .close().extrude(1.25, both=True)
               .translate((xr, 0, 0)))
        s_ = s_.union(rib)

    # 斜面法向（朝外）；钻孔沿 -n_out 钻入楔内
    n_in = (0.0, -c, -s)

    # 托盘螺丝导孔（φ2.6×8，M3 自攻）
    for x in (-(bw/2 - 18), bw/2 - 18):
        for d in (18.0, 118.3):
            y = bd - d*s; z = d*c
            pln = cq.Plane(origin=(x, y, z), xDir=(1, 0, 0), normal=n_in)
            s_ = s_.cut(cq.Solid.makeCylinder(1.3, 8).located(cq.Location(pln)))

    # 墙面固定孔（M4 沉头，钻穿到贴墙面；沉头锥埋在斜面）
    for x in (-44.0, 44.0):
        for d in (60.0, 118.3):
            y = bd - d*s; z = d*c
            depth = y/c + 2 - 2.2           # 钻到贴墙面，多 2mm 导向
            pln = cq.Plane(origin=(x, y, z), xDir=(1, 0, 0), normal=n_in)
            cone = cq.Solid.makeCone(8.6/2, 4.5/2, 2.21)
            cyl  = cq.Solid.makeCylinder(4.5/2, depth).translate((0, 0, 2.2))
            s_ = s_.cut(cone.fuse(cyl).located(cq.Location(pln)))

    return s_


# =============================================================
# 4. 球头底座（吊顶用，含 1/4" 热熔嵌件座）
# =============================================================
def ball_base():
    pw, ph, bt = 70.0, 70.0, BASE_T
    s = (cq.Workplane("XY").box(pw, ph, bt)
         .edges("|Z").fillet(R_BASE)
         .translate((0, 0, bt/2)))
    boss = (cq.Workplane("XY").circle((QUARTER_D+10)/2)
            .extrude(QUARTER_H)
            .translate((0, 0, bt)))
    s = s.union(boss)
    # 热熔嵌件孔（φ8.2×8，从座体外端压入）+ 螺丝通过孔
    s = s.cut(cq.Workplane("XY").circle(INSERT_D/2).extrude(INSERT_H + 1)
              .translate((0, 0, bt + QUARTER_H - INSERT_H)))
    s = s.cut(cq.Workplane("XY").circle(QUARTER_D/2)
              .extrude(bt + QUARTER_H - INSERT_H + 1)
              .translate((0, 0, -1)))
    # 4 个固定孔
    for dx in (-1, 1):
        for dy in (-1, 1):
            s = s.cut(cq.Workplane("XY")
                      .center(dx*(pw/2-10), dy*(ph/2-10))
                      .circle(2.25).extrude(bt + 2)
                      .translate((0, 0, -1)))
    return s


# =============================================================
if __name__ == "__main__":
    print("生成 STEP 文件 →", OUT)
    print("\n[平板假体]")
    export(tablet_dummy(hollow=False, finger=True), "dummy-tablet-solid")
    export(tablet_dummy(hollow=True,  finger=True), "dummy-tablet-hollow")

    print("\n[托盘]")
    export(tray(hook_slot=False), "tray-tablet-8in")
    export(tray(hook_slot=True),  "tray-tablet-8in-hook")

    print("\n[底座]")
    ow = TAB_W + CLEAR*2 + WALL_TH*2
    oh = LIP_H + TAB_H + CLEAR*2 + CLAMP_H + WALL_TH
    export(wedge_base(ow, oh, 22.0), "base-wedge-22deg")
    export(wedge_base(ow, oh, 20.0), "base-wedge-20deg")
    export(ball_base(), "base-ball-quarter")
    print("\n完成。STEP 可直接拖进 Shapr3D 编辑。")
