# N100 中枢与 HA

N100 迷你主机运行 Home Assistant，负责统一 UI、历史与能源面板、远程访问、通知和非关键高阶自动化。**HA 不承载安全关键自动化**（留在 ESPHome 边缘）。

| 文件 | 内容 |
|------|------|
| [design.md](design.md) | HA 角色边界（定稿原则）、N100 主机、网络、安卓车机、平板 |
| [tablet-mount.md](tablet-mount.md) | **平板支架（三处）**：水槽前 + 额头柜下沿 + **吊顶悬吊**；3D 打印斜角件、倾角测算、旋转结构对比 |
| [tablet-mount.scad](tablet-mount.scad) | **参数化 OpenSCAD 脚本**：改数值即出 STL（wall / ceiling 两种模式） |
| [tablet.md](tablet.md) | 小米平板4 移动位（副驾/后床旁）+ 直供电改造（**暂缓**） |
| [bom.md](bom.md) | 材料清单 |

## 边界

- 待定决策（远程访问方式、常开策略等）集中记录在 design.md，不另起文档
