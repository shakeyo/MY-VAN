# 柜体与台面

全车木工柜体，包含额头柜面板与右侧阶梯柜排。柜体是房车最占体积的部分，设计不当要么储物不够、要么过道太窄。本方案将右侧柜排沿车厢纵深分为**台面段**（水槽+电磁炉+操作区）和**床段柜**（储物+夜间承床），两段高度错落——台面段 850mm 操作高度，床段柜顶与床基座等高。

**核心思路**：一柜多用。额头柜不仅是储物，还是前声场喇叭箱体；床段柜不仅是柜子，还是抽拉床的承重端。所有柜体通过角码+螺栓固定于预埋点，年审可拆。

## 子系统

| 文件 | 内容 | 状态 |
|------|------|------|
| [design-overhead.md](design-overhead.md) | 额头柜面板（含喇叭开孔） | 设计中 |
| [design-countertop.md](design-countertop.md) | 右侧台面段（水槽 + 电磁炉 + 柜体） | 待设计 |
| [design-bed-cabinet.md](design-bed-cabinet.md) | 右侧床段柜（储物 + 夜间承床） | 待设计 |

## 跨模块依赖

- 柜体锚固点由 01-vehicle-layout 预埋
- 台面段水槽接入 [05-water-system](../05-water-system/)
- 台面段电磁炉接入 [04-power-system](../04-power-system/)
- 床段柜顶高度 = [08-bed-and-seat](../08-bed-and-seat/) 床基座高度（需等高）
- 音响设计见 [11-entertainment](../11-entertainment/)，本模块仅负责面板木工及喇叭物理安装位

## BOM

统一材料清单见 [bom.md](bom.md)。

## 图片

<script setup>
const loaders = Object.values(import.meta.glob('./assets/*.{png,jpg,jpeg,PNG,JPG,JPEG,webp}', { eager: false }))
</script>

<AutoGallery :loaders="loaders" />
