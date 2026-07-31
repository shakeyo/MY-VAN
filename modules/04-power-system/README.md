# 电力系统

48V 磷酸铁锂主电池 + 多源充电 + 星型配电的整车电力架构。选择 48V 而非 12V 的核心原因：同等功率下电流降为 1/4，线损降为 1/16，可以用更细的线缆走更长的车内距离。12V 仅通过 DCDC 降压模块供照明、风扇、控制等小功率回路。

**核心思路**：星型拓扑 + 源头熔断 + 模块化隔离。每一路从配电箱独立出线，不串接；每个回路在保险盒源头独立保护；48V 动力回路与 12V 控制回路物理分区。

## 子文档

| 文件 | 内容 | 状态 |
|------|------|------|
| [design.md](design.md) | 系统架构：48V 电池、充放电、布线规范 | 设计中 |
| [design-distribution-box.md](design-distribution-box.md) | 中门智能配电箱：48V/12V 配电、继电器、端子排、12 芯线标准 | 设计中 |
| [bom.md](bom.md) | 材料清单 | 待补充 |

## 子系统

| 子系统 | 说明 | 状态 |
|--------|------|------|
| 48V 电池组 | 磷酸铁锂 16S，BMS，低温保护 | 设计中 |
| 多源充电 | 行车充电（DC-DC）、太阳能（MPPT）、市电快充 | 设计中 |
| 星型配电 | 中门配电箱 + 48V 保险盒 + 12V 保险盒 | 设计中 |
| 12V 子系统 | DCDC 降压、照明/通风/冰箱/控制供电 | 设计中 |
| 逆变器 | 48V→220V 纯正弦波，AC 插座回路 | 待设计 |

## 跨模块依赖

- 48V 电池安装位由 [01-vehicle-layout](../01-vehicle-layout/) 预埋锚固点
- 太阳能板电气接入来自 [02-external](../02-external/)
- 水泵供电接 [05-water-system](../05-water-system/)
- 空调/暖风供电接 [06-hvac](../06-hvac/)
- 整车走线需与所有模块协同预留

## BOM

统一材料清单见 [bom.md](bom.md)。

## 图片

<script setup>
const loaders = Object.values(import.meta.glob('./assets/*.{png,jpg,jpeg,PNG,JPG,JPEG,webp}', { eager: false }))
</script>

<AutoGallery :loaders="loaders" />
