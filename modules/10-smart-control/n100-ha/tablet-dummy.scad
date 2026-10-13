// =============================================================
// 平板假体（dummy tablet）—— 用于【打印前试装】
//   按小米平板4 8" 实测尺寸做替身，验证：
//     1. 托盘内腔尺寸是否合适（取放松紧）
//     2. 倾角/安装位置/视角（比划着看）
//     3. 收纳挂槽好不好挂
//
//   ⚠ 不是真机能替代品：只验证【几何】，不验证重量手感
//     若要模拟重量，可把 hollow=false + 高填充，或内部塞配重
//
// 用法：改 PARAMS → F6 → Export STL
// =============================================================

// ---------- 输出选择 ----------
PART     = "tablet";   // "tablet" 平板假体 | "gauge" 厚度卡规

// ---------- 平板尺寸（改这里适配你的机器）----------
tab_w   = 200.2;   // 宽
tab_h   = 120.3;   // 高
tab_t   = 7.9;     // 厚

// ---------- 形式 ----------
hollow   = true;   // true 薄壳空心（省料）| false 实心砖（模拟重量）
shell_t  = 1.6;    // 空心时壳厚
rib_n    = 3;      // 内部加强筋数量（空心时）

// ---------- 便利特征 ----------
finger_hole  = true;   // 背面指孔（方便取放测试）
fh_d         = 22;     // 指孔直径
corner_r     = 8;      // 四角圆角（模仿真机手感）

$fn = 64;

// ---------- 主体 ----------
module body() {
    if (hollow) {
        difference() {
            // 外形
            round_box(tab_w, tab_h, tab_t, corner_r);
            // 掏空（留壳厚）
            translate([shell_t, shell_t, shell_t])
                round_box(tab_w - shell_t*2, tab_h - shell_t*2,
                          tab_t, corner_r - shell_t);
        }
        // 内部加强筋
        for (i = [0 : rib_n-1]) {
            x = tab_w*(i+1)/(rib_n+1);
            translate([x - 1, shell_t, shell_t])
                cube([2, tab_h - shell_t*2, tab_t - shell_t*2]);
        }
    } else {
        round_box(tab_w, tab_h, tab_t, corner_r);
    }
}

// 圆角方块
module round_box(w, h, t, r) {
    hull() {
        for (dx = [-1, 1]) for (dy = [-1, 1])
            translate([w/2 + dx*(w/2 - r), h/2 + dy*(h/2 - r), 0])
                cylinder(r = r, h = t);
    }
}

// ---------- 背面指孔（取放用）----------
// ⚠ 必须是【减料】：用 difference 从本体挖穿
//    早期写成 union 会变成一个凸台（还让总厚变成 9.9）
module finger() {
    // 一个长圆孔，靠近上边中部——方便拇指顶出平板
    translate([tab_w/2, tab_h - 28, -1])
        hull() {
            cylinder(d = fh_d, h = tab_t + 2);
            translate([0, -14, 0]) cylinder(d = fh_d, h = tab_t + 2);
        }
}

// 指孔周围的加强环（空心件孔边只有 1.6mm，反复取放会裂）
module finger_rib() {
    if (hollow) {
        translate([tab_w/2, tab_h - 28, shell_t])
            difference() {
                hull() {
                    cylinder(d = fh_d + 7, h = tab_t - shell_t*2);
                    translate([0, -14, 0]) cylinder(d = fh_d + 7, h = tab_t - shell_t*2);
                }
                hull() {
                    cylinder(d = fh_d, h = tab_t);
                    translate([0, -14, 0]) cylinder(d = fh_d, h = tab_t);
                }
            }
    }
}

// ---------- 配件：厚度卡规（验内腔松紧）----------
// 打 3 个不同厚度的薄片，插进托盘试松紧：7.9 / 8.4 / 8.9
module gauge_stack() {
    gap = 4;
    for (i = [0:2]) {
        th = tab_t + i*0.5;
        translate([i*(40+gap), 0, 0]) {
            difference() {
                cube([40, 30, th]);
                translate([6, 6, -1]) cube([28, 18, th+2]);  // 掏成框
            }
        }
    }
}

// ---------- 输出 ----------
module final() {
    difference() {
        union() {
            body();
            if (finger_hole) finger_rib();   // 先加加强环
        }
        if (finger_hole) finger();           // 再挖穿指孔
    }
}

if (PART == "gauge") gauge_stack(); else final();
