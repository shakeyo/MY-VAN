// =============================================================
// 平板壁挂/悬吊支架 —— 参数化 OpenSCAD
//   小米平板4 8": 200.2 × 120.3 × 7.9 mm
//
// 用法：改下面 PARAMS 里的数值 → Render (F6) → Export STL
//   两处用途：
//     ① 水槽前壁挂（mod = "wall"）：固定倾角楔形，屏幕面朝上后
//     ② 吊顶悬吊（mod = "ceiling"）：屏幕面朝下前，配球头/齿盘调角
//
// 注意：本脚本只做【平板壳 + 托边/压边】。底板/球头接口是独立件，见文件末。
// =============================================================

// ---------- PARAMS ----------
mod          = "wall";   // "wall" 水槽前 | "ceiling" 吊顶

tab_w        = 200.2;    // 平板宽（横屏）
tab_h        = 120.3;    // 平板高
tab_t        = 7.9;      // 平板厚
clear        = 1.0;      // 单侧取放间隙

wall_th      = 3.0;      // 壳体壁厚
lip_depth    = 5.0;      // 底部托边深度（承重）
lip_height   = 8.0;      // 底部托边高度
clamp_h      = 3.0;      // 顶部压边包覆量
back_t       = 3.0;      // 背板厚

tilt         = 22;       // 倾角（度）——水槽前 20-22；吊顶按视角算（14-48）
rib_count    = 3;        // 加强筋数量
rib_th       = 2.5;      // 加强筋厚

// 球头/齿盘接口（mod="ceiling" 或想调角时）
add_mount    = false;    // true = 背板加 1/4" 螺母座
quarter_d    = 6.35;     // 1/4" = 6.35mm
quarter_h    = 9.0;      // 螺母座高（用热熔铜螺母埋入）

// ---------- 收纳（吊顶用）----------
stow         = "none";   // "none" 不收纳 | "hook" 挂墙钩（推荐）| "hinge" 上翻贴顶
hook_len     = 30;       // L 型挂钩伸出长度
hook_d       = 5;        // 挂钩直径（配合壳背面的挂槽）

$fn = 48;

// ---------- 派生尺寸 ----------
iw = tab_w + clear*2;                       // 内腔宽
ih = tab_h + clear*2;                       // 内腔高
ow = iw + wall_th*2;                        // 外廓宽
// 外廓高 = 下托边 + 内腔高 + 顶部压边悬垂 + 顶壁
// ⚠ 必须含 clamp_h：否则内腔顶到顶面，压边没有包覆平板的悬垂量
oh = lip_height + ih + clamp_h + wall_th;

echo(str("内腔: ", iw, " × ", ih, " mm"));
echo(str("外廓: ", ow, " × ", oh, " mm"));
echo(str("顶部撑出(倾角", tilt, "°): ", oh*sin(tilt), " mm"));

// ---------- 主体 ----------
module shell() {
    difference() {
        // 外壳
        cube([ow, oh, tab_t + lip_depth + back_t]);
        // 内腔（前方开口）
        // 顶面 = lip_height + ih，其上是 clamp_h 悬垂 + 顶壁
        translate([wall_th, lip_height, back_t])
            cube([iw, ih, (tab_t + lip_depth + back_t)*2]);
    }
}

// 底部托边（承重）：平板坐落其上
module lip() {
    translate([wall_th, 0, back_t])
        cube([iw, lip_height, lip_depth + tab_t]);
}

// 顶部压边：从内腔顶再向上 clamp_h 悬垂，包住平板上沿
module clamp() {
    translate([wall_th, lip_height + ih, back_t])
        cube([iw, clamp_h + wall_th, tab_t + clamp_h]);
}

// 加强筋（背面，提高抗弯）
module ribs() {
    for (i = [0 : rib_count-1]) {
        x = wall_th + iw*(i+1)/(rib_count+1);
        translate([x - rib_th/2, 0, 0])
            cube([rib_th, oh, 6]);
    }
}

// 散热孔阵列
module vents() {
    for (r = [0:3]) for (c = [0:7]) {
        translate([wall_th + 8 + c*((iw-16)/7), lip_height + 10 + r*((ih-20)/3), -1])
            cylinder(d = 4, h = back_t + 2);
    }
}

// 1/4" 螺母座（背面中心，埋热熔铜螺母）
module quarter_mount() {
    translate([ow/2, oh/2, 0])
        difference() {
            cylinder(d = quarter_d + 8, h = quarter_h + back_t);
            translate([0,0,-1]) cylinder(d = quarter_d, h = quarter_h + back_t + 2);
        }
}

// ---------- 收纳：壳背面的【挂槽】（配顶棚 L 型挂钩）----------
// 用法：收纳时把平板壳挂到顶棚旁的 L 型钩上
// 挂槽做成【上开口的燕尾槽】，靠平板自重卡住，抖动不脱
module hook_slot() {
    translate([ow/2, oh - 30, -hook_d/2])
        difference() {
            // 槽体（凸出背板）
            cube([hook_d*2.4, 12, hook_d*1.2], center = true);
            // 槽口（开口向上，容纳 hook_d 直径的钩）
            translate([0, 0, hook_d*0.1])
                rotate([90, 0, 0])
                    cylinder(d = hook_d + 0.4, h = 14, center = true);
        }
}

// ---------- 独立件：顶棚 L 型挂钩（收纳用，另打 2 个）----------
module ceiling_hook() {
    // 底板（贴顶棚，2 个螺丝孔）
    difference() {
        cube([26, 4, hook_len + 6]);
        translate([6.5, -1, hook_len - 4]) rotate([-90,0,0]) cylinder(d=3.2, h=6);
        translate([19.5, -1, hook_len - 4]) rotate([-90,0,0]) cylinder(d=3.2, h=6);
    }
}

// ---------- 组装 ----------
module build() {
    difference() {
        union() {
            shell();
            lip();
            clamp();
            ribs();
        }
        vents();
    }
    if (add_mount) quarter_mount();
    if (stow == "hook") hook_slot();
}

// ---------- 倾角与摆放 ----------
// 屏幕面朝上后（wall）：绕底边旋转 tilt
// 屏幕面朝下前（ceiling）：绕顶边反向旋转
rotate([mod == "wall" ? tilt : -tilt, 0, 0])
    build();

// ---------- 收纳挂钩（要打 2 个时取消注释）----------
// ceiling_hook();

// =============================================================
// 【打印方向】贴墙面/贴顶面朝下（Z=0 平面），层纹垂直于受力 → 强度最高
//   - wall 模式：背板朝下打印，斜面朝上可免支撑
//   - ceiling 模式：背板（贴顶面）朝下打印
//
// 【独立件】球头/齿盘接口底座（若 add_mount=true 则壳体自带螺母座）
//   吊顶悬吊建议：1/4" 球头（带锁紧旋钮）或齿盘式俯仰关节
//   理由：坐姿观看位置不同，所需倾角 14-48°，跨度 35°，【必须可调】
//
// 【材料】PETG（车内暴晒 60-70°C，纯 PLA 会软化）
//   填充 30-40%，壁厚 3mm
// =============================================================
