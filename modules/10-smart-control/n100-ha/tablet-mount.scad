// =============================================================
// 平板支架（水槽前 / 额头柜下 / 吊顶）—— 参数化 OpenSCAD
//   小米平板4 8": 200.2 × 120.3 × 7.9 mm，横屏使用
//
// 【设计要点：两件式，不是旋转整体】
//   件1 托盘 tray  —— 直立开口托盘，倾角由【底座】提供，背板平贴底座斜面
//   件2 底座 base  —— 楔形（wall 模式，贴墙面）或球头座（ceiling 模式）
//   两件用 4×M3 沉头自攻螺丝连接（托盘背面沉孔 ↔ 底座斜面导孔）
//
//   压边 = L 形（前唇 + 横梁）：前唇压住平板上沿 2mm，横梁防脱出
//   （取放：底部先斜插进托边，上沿压入前唇下方）
//
// 用法：改 PARAMS → F6 渲染 → Export STL，分别导出 tray 和 base
//   导出哪个由 PART 决定（"tray" / "base" / "both"）
// =============================================================

// ---------- 导出选择 ----------
PART         = "tray";   // "tray" 托盘 | "base" 底座 | "both" 拼一起看

// ---------- 安装方式 ----------
mod          = "wall";   // "wall" 壁挂（水槽前/额头柜下）| "ceiling" 吊顶悬吊

// ---------- 平板尺寸 ----------
tab_w        = 200.2;
tab_h        = 120.3;
tab_t        = 7.9;
clear        = 1.0;      // 单侧取放间隙

// ---------- 托盘参数 ----------
wall_th      = 3.0;
lip_depth    = 5.0;      // 底部托边深度
lip_height   = 8.0;      // 底部托边高度
clamp_h      = 3.0;      // 压边前唇厚度（Z 向）
clamp_grip   = 2.0;      // 压边前唇压住平板上沿的量（Y 向）
back_t       = 3.0;      // 背板厚
fillet_r     = 3.0;      // 内腔四角圆角（≤4 才不与平板 R8 圆角干涉）

// ---------- 底座参数 ----------
base_t       = 6.0;      // 底座板厚
tilt         = 22;       // 倾角（wall 用）；ceiling 不需要
quarter_d    = 6.35;     // 1/4" 螺丝通过孔
insert_d     = 8.2;      // 1/4 热熔铜螺母嵌件孔（嵌件外径 8.4）
insert_h     = 8.0;      // 嵌件孔深
quarter_h    = 9.0;      // 1/4 螺母座高

// ---------- 收纳 ----------
stow         = "hook";   // "none" | "hook" 挂槽+1/4 螺母座（吊顶收纳用）
hook_d       = 5.0;      // 挂钩直径
hook_offset  = 38.0;     // 挂槽中心距托盘顶（避开 1/4 座）

$fn = 48;

// ---------- 派生 ----------
iw = tab_w + clear*2;
ih = tab_h + clear*2;
ow = iw + wall_th*2;
oh = lip_height + ih + clamp_h + wall_th;
depth = tab_t + lip_depth + back_t;

// ---------- 楔形底座派生（辅助模块要用，必须全局）----------
w_t     = 5;                 // 楔形壁厚
w_TRUNC = 4;                 // 顶部截平量（去刀口）
w_bd    = oh * tan(tilt);    // 进深
w_s     = sin(tilt);
w_c     = cos(tilt);
// 等距掏空：内三角顶点 = 斜面/贴墙面/底面各内缩 w_t 的交点
w_z_apex  = (w_bd*w_c - w_t*(1+w_c)) / w_s;
w_y_front = (w_bd*w_c - w_t*(1+w_s)) / w_c;

echo(str("内腔: ", iw, " × ", ih, " mm"));
echo(str("托盘外廓: ", ow, " × ", oh, " × ", depth, " mm"));

// =============================================================
// 件1：托盘（直立，背板朝下平放打印，开口朝上）
// =============================================================
module tray() {
    bar_y = lip_height + ih - clear;          // 压边横梁内面（平板上沿 + 1mm 余量）

    difference() {
        union() {
            cube([ow, oh, depth]);
        }
        // 内腔（前开口）
        translate([wall_th, lip_height, back_t])
            cube([iw, ih, depth*2]);
        // 散热孔（背板）
        for (r = [0:3]) for (c = [0:7]) {
            translate([wall_th + 8 + c*((iw-16)/7),
                       lip_height + 10 + r*((ih-20)/3), -1])
                cylinder(d = 4, h = back_t + 2);
        }
        // 侧壁通风槽（壁挂时背板被底座挡住，靠侧槽对流）
        for (y0 = [28, 62, 96]) {
            translate([-0.5, y0, back_t]) cube([wall_th + 1, 3, depth - back_t]);
            translate([ow - wall_th - 0.5, y0, back_t]) cube([wall_th + 1, 3, depth - back_t]);
        }
        // 走线缺口（两侧都开：横屏充电口可能在任一侧）
        for (sx = [-0.5, ow - wall_th - 0.5])
            translate([sx, 14, back_t]) cube([wall_th + 1, 12, 11]);
        // 4×M3 沉头孔（连接底座，从内腔侧钻，沉头与背板内面齐平）
        for (dx = [-1, 1]) for (dy = [-1, 1]) {
            translate([ow/2 + dx*(ow/2 - 18), oh/2 + dy*(oh/2 - 18), 0]) {
                translate([0, 0, back_t - 1.9]) cylinder(d1 = 6.2, d2 = 3.2, h = 1.9 + 0.01);
                translate([0, 0, -1]) cylinder(d = 3.2, h = back_t + 1.2);
            }
        }
    }
    // 压边前唇（压住平板上沿 clamp_grip）
    translate([wall_th, lip_height + tab_h - clamp_grip, back_t + tab_t])
        cube([iw, clamp_grip + clear, clamp_h]);
    // 压边横梁（防脱出）
    translate([wall_th, bar_y, back_t])
        cube([iw, oh - bar_y, depth - back_t]);
    // 内腔四角圆角（减应力集中；给平板 R8 圆角让位）
    for (cx = [wall_th, ow - wall_th]) for (cy = [lip_height, lip_height + ih])
        translate([cx, cy, 0]) cylinder(r = fillet_r, h = depth);
    // 吊顶：1/4" 热熔螺母座（背面中心，壁挂款不加）
    if (stow == "hook") quarter_seat();
}

// 1/4" 螺母座：φ20×10 座 + 热熔嵌件孔 φ8.2×8 + 螺丝通过孔
module quarter_seat() {
    difference() {
        translate([ow/2, oh/2, -10]) cylinder(d = 20, h = 10);
        translate([ow/2, oh/2, -9.5]) cylinder(d = insert_d, h = insert_h + 0.5);
        translate([ow/2, oh/2, -2]) cylinder(d = quarter_d, h = 5.5);
    }
}

// 收纳挂槽（在托盘背面）
module tray_hook_slot() {
    translate([ow/2, oh - hook_offset, -hook_d*0.6])
        difference() {
            cube([hook_d*2.4, 12, hook_d*1.2], center = true);
            translate([0, 0, hook_d*0.1])
                rotate([90, 0, 0]) cylinder(d = hook_d + 0.4, h = 14, center = true);
        }
}

// =============================================================
// 件2a：楔形底座（wall 模式）
//   剖面（Y-Z，Y=进深，Z=高度）：
//     (0, 0) 贴墙底角 → (0, bh) 贴墙顶角 → (bd, 0) 前伸底角
//   贴墙面 = Y=0 竖直面；斜面从顶到底，tan(θ) = bd / bh
//   内部：等距掏空（斜面平行偏移 5mm，顶部实心）+ 3 道竖向筋
// =============================================================
module wedge_base() {
    bw = ow;                                  // 与托盘同宽
    bh = oh;                                  // 与托盘等高
    bd = w_bd;                                // 进深由倾角决定
    t  = w_t;                                 // 壁厚
    TRUNC = w_TRUNC;
    s  = w_s; c = w_c;
    z_apex  = w_z_apex;                       // 内三角顶角 Z
    y_front = w_y_front;                      // 内三角前底角 Y

    echo(str("楔形底座: 宽", bw, " 高", bh, " 进深", bd,
             " (倾角", tilt, "°)"));

    difference() {
        union() {
            difference() {
                polyhedron(
                    points = [
                        [0,0,0], [bw,0,0],            // 0,1 贴墙底
                        [0,0,bh], [bw,0,bh],          // 2,3 贴墙顶
                        [0,bd,0], [bw,bd,0]           // 4,5 前伸底
                    ],
                    faces = [
                        [0,2,3,1],                    // 贴墙面 (Y=0)
                        [0,1,5,4],                    // 底面
                        [2,4,5,3],                    // 斜面
                        [0,4,2],                      // 左侧三角
                        [1,3,5]                       // 右侧三角
                    ],
                    convexity = 4
                );
                polyhedron(
                    points = [
                        [t,t,t], [bw-t,t,t],          // 内贴墙底
                        [t,t,z_apex], [bw-t,t,z_apex],// 内贴墙顶
                        [t,y_front,t], [bw-t,y_front,t] // 内前底
                    ],
                    faces = [
                        [0,2,3,1], [0,1,5,4], [2,4,5,3], [0,4,2], [1,3,5]
                    ],
                    convexity = 4
                );
            }
            // 内部竖向筋（Y-Z 板，撑住斜面 + 给螺丝加肉）
            rib(52.05); rib(104.1); rib(156.15);
        }
        // 顶部截平（去刀口，打印末端不再有发丝层）
        translate([-1, -1, bh - TRUNC - 0.01]) cube([bw + 2, bd + 2, TRUNC + 1]);
        // 托盘螺丝导孔（φ2.6×8，法向钻入，M3 自攻）
        for (x = [18, bw - 18]) for (d = [18, 118.3])
            hole_normal(x, d, 2.6, 8);
        // 墙面固定孔（M4 沉头，法向钻穿到贴墙面）
        for (x = [60.1, bw - 60.1]) for (d = [60, 118.3])
            csk_normal(x, d, 4.5, 8.6, 2.2);
    }
}

// 内部筋：Y-Z 平面三角板，厚 2.5，位于楔形 X = x
module rib(x) {
    translate([x, 0, 0])
        rotate([0, -90, 0])
            linear_extrude(2.5)
                polygon([[0, 0], [0, w_bd], [oh - w_TRUNC, 0]]);
}

// 沿斜面法向钻孔（d = 距斜面底边的距离，len = 孔深，从斜面向楔内钻）
//   法向 = (0, c, s)，钻入方向 = rotate([90+tilt,0,0]) 的 +Z = (0, -c, -s)
module hole_normal(x, d, dia, len) {
    y = w_bd - d*w_s; z = d*w_c;
    translate([x, y, z]) rotate([90 + tilt, 0, 0])
        cylinder(d = dia, h = len, $fn = 32);
}

// 沿斜面法向钻沉头孔（沉头锥开在斜面上，钻穿贴墙面，多 2mm 导向）
module csk_normal(x, d, dia, csk_dia, csk_h) {
    y = w_bd - d*w_s; z = d*w_c;
    len = y / w_c + 2;
    translate([x, y, z]) rotate([90 + tilt, 0, 0]) {
        cylinder(d1 = csk_dia, d2 = dia, h = csk_h + 0.01);
        cylinder(d = dia, h = len, $fn = 32);
    }
}

// =============================================================
// 件2b：球头底座（ceiling 模式）
//   贴顶棚平板 + 中心 1/4" 热熔嵌件座（嵌件外径 8.4，孔 φ8.2）
// =============================================================
module ball_base() {
    pw = 70; ph = 70;
    difference() {
        union() {
            translate([-pw/2, -ph/2, 0]) cube([pw, ph, base_t]);
            translate([0, 0, base_t]) cylinder(d = quarter_d + 10, h = quarter_h);
        }
        // 热熔嵌件孔（从座体外端压入）
        translate([0, 0, base_t + quarter_h - insert_h])
            cylinder(d = insert_d, h = insert_h + 1);
        // 1/4" 螺丝通过孔
        translate([0, 0, -1])
            cylinder(d = quarter_d, h = base_t + quarter_h - insert_h + 1);
        // 4 个固定孔（拧顶棚）
        for (dx = [-1, 1]) for (dy = [-1, 1])
            translate([dx*(pw/2-10), dy*(ph/2-10), -1])
                cylinder(d = 4.5, h = base_t + 2);
    }
}

// =============================================================
// 输出
// =============================================================
if (PART == "tray") {
    tray();
    if (stow == "hook") tray_hook_slot();
} else if (PART == "base") {
    if (mod == "wall") wedge_base(); else ball_base();
} else {
    // both：拼一起看装配关系（仅预览，不用于打印）
    if (mod == "wall") {
        // 楔形底座：贴墙面 Y=0 在原点，斜面朝 +Y
        // 托盘绕 (0, sin(45-tilt/2), cos(45-tilt/2)) 轴翻转 180°，
        // 背板平贴斜面、开口朝房间（+Y）
        wedge_base();
        translate([ow, w_bd, 0])
            rotate(v = [0, sin(45 - tilt/2), cos(45 - tilt/2)], a = 180) {
                tray();
                if (stow == "hook") tray_hook_slot();
            }
    } else {
        // 球头底座：示意在托盘背后（实际通过球头连接，非直接贴合）
        tray();
        if (stow == "hook") tray_hook_slot();
        translate([ow/2, -depth - 25, oh/2])
            rotate([90, 0, 0])
                ball_base();
    }
}

// =============================================================
// 【打印方向】全部背板/贴墙面朝下平放（层纹⊥受力，免支撑）
//   tray：背板朝下（开口朝上）；挂槽/螺母座在背面随首层打印
//   base(wall)：贴墙面朝下，斜面 68° 自支撑
//   base(ceiling)：贴顶面朝下，座体朝上
//
// 【材料】PETG（车内暴晒 60-70°C，纯 PLA 会软化）；填充 30-40%
//
// 【装配】
//   壁挂：楔形底座先用 4×M4 木螺丝上墙（M4×50 下排 / M4×25 上排，
//         沉头埋入斜面）→ 托盘 4×M3×10 沉头自攻拧入斜面导孔
//   吊顶：球头底座 4×M4 上顶棚（1/4 嵌件压入座体）→ 球头公头拧进
//         托盘背面 1/4 嵌件；收纳时整体旋下挂到顶棚旁 L 型钩
// =============================================================
