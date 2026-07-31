# 用水系统

清水 → 用水点 → 灰水箱的完整水路。房车水路不同于家装：车辆颠簸要求所有接头带锁止、水箱需防浪板、冬季需排空防冻。因此全车采用快接水路，便于年审时断开管路拆卸水箱。

**核心思路**：快接化 + 模块化。水泵与水箱之间、水箱与用水点之间全部用快插接头，不用生料带+螺纹硬接。排水重力自流，不设电动排水泵。

## 子文档

| 文件 | 内容 | 状态 |
|------|------|------|
| [design.md](design.md) | 系统设计：水箱、水泵、管路、排水 | 设计中 |
| [bom.md](bom.md) | 材料清单 | 待补充 |

## 子系统

| 子系统 | 说明 | 状态 |
|--------|------|------|
| 清水箱 | PE 食品级水箱，防浪板，液位传感器 | 设计中 |
| 灰水箱 | 重力排水，可拆卸清洗 | 待设计 |
| 水泵 | 48V 隔膜泵，经配电箱继电器控制 | 设计中 |
| 快接管路 | 快插接头 + PEX/PU 管，全车水路 | 设计中 |
| 排水 | 台盆 + 淋浴地漏 → 灰水箱，重力自流 | 待设计 |

## 跨模块依赖

- 水箱安装位由 [01-vehicle-layout](../01-vehicle-layout/) 和 [00-chassis](../00-chassis/) 预埋挂架
- 水泵供电及控制由 [04-power-system](../04-power-system/) 中门配电箱接管
- 台面水槽由 [07-cabinetry](../07-cabinetry/) 提供安装位
- 淋浴排水接入 [09-shower-module](../09-shower-module/)

## BOM

统一材料清单见 [bom.md](bom.md)。

## 图片

<script setup>
const loaders = Object.values(import.meta.glob('./assets/*.{png,jpg,jpeg,PNG,JPG,JPEG,webp}', { eager: false }))
</script>

<AutoGallery :loaders="loaders" />
