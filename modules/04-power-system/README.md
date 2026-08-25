# 电力系统

48V 磷酸铁锂主电池 + 多源充电 + 星型配电的整车电力架构。选择 48V 而非 12V 的核心原因：同等功率下电流降为 1/4，线损降为 1/16，可以用更细的线缆走更长的车内距离。12V 仅通过 DCDC 降压模块供照明、风扇、冰箱、控制等小功率回路。

**核心思路**：星型拓扑 + 源头熔断 + 模块化隔离。每一路从配电箱独立出线，不串接；每个回路在保险盒源头独立保护；48V 动力回路与 12V 控制回路物理分区。

## 📖 施工阅读指南（按顺序读）

| 顺序 | 文档 | 看什么 |
|------|------|--------|
| 1 | [build-guide.md](build-guide.md) | **施工主线**：6 个阶段按序执行，每阶段有入口条件 / 验收点 / 配图 |
| 2 | [design.md](design.md) | 设计原则：为什么 48V、为什么星型、源头保护链路、施工红线 |
| 3 | [design-distribution-box.md](design-distribution-box.md) | 中门配电箱：箱内布局、48V/12V 保险分配、继电器与端子排、箱内施工步骤 1-10 |
| 4 | [switch-assignment.md](switch-assignment.md) | 面板按键 ↔ IO 通道 ↔ 负载继电器对照、14 芯线线色、端子排位 |
| 5 | [bom.md](bom.md) | 材料清单：开工前照单采购（含液压压线钳等工具） |

## 🏗️ 施工主线（6 阶段，详见 [build-guide.md](build-guide.md)）

| 阶段 | 目标 | 出口验收（做到才能进下一阶段） |
|------|------|------------------------------|
| 0 准备 | 采购齐 + **家里预制负载线束**（裁线/压端子/焊并/贴标签） | 每根线两端有标签，端子排/保险盒就位 |
| 1 电池与总保护 | 电池安装 + 源头熔断 150A + 主断 125A（电池侧） | 绝缘无碰壳、铜鼻扭矩达标、主断可分断 |
| 2 中门配电箱 | 按箱内步骤 1-10 接线（负汇流 → 48V 主干 → DCDC → 12V 分配 → 继电器 → 控制 → 信号 → 出线 → 整理标识） | §十二安全检查清单全过 + 未通电逐路测短路 |
| 3 面板与线缆 | 按钮接线、焊并点、14P/8P 插头压接、入面板插座 | 逐芯通断测试通过，LED 极性确认 |
| 4 485 总线 + ESP32 | 菊花链并线、两端 120Ω、强弱电分离 | 总线 A/B 无短接，模块地址正确 |
| 5 分阶段通电 | 48V 总进线 → DCDC 输出 → 控制模块 → 灯 → 风扇 → 冰箱 → **水泵最后** | 逐段电压正常，水泵试车（二极管方向已核） |

## 🖼️ 配图索引（全部在本模块 `diagrams/`）

| 图 | 文件 | 什么时候看 |
|----|------|-----------|
| 整车电力架构单线图 | [power-architecture.svg](./diagrams/power-architecture.svg) | 开工前理解全局电流走向 |
| 中门箱内布局（正视图） | [box-layout.svg](./diagrams/box-layout.svg) | 阶段 2：箱内器件定位 |
| 48V 水泵主回路 + 控制回路 | [pump-48v.svg](./diagrams/pump-48v.svg) | 阶段 2/5：核心安全回路 |
| 单按键 3 回路（含"两个 COM"辨析） | [button-wiring.svg](./diagrams/button-wiring.svg) | 阶段 3：面板接线前 |
| 14 芯线线色/芯位对照 | [14core-cable.svg](./diagrams/14core-cable.svg) | 阶段 3：压插头、按色找芯 |
| 端子排布局（功率区 + 控制区） | [terminal-block.svg](./diagrams/terminal-block.svg) | 阶段 2/3：对位接线 |
| 485 总线拓扑 | [485-bus.svg](./diagrams/485-bus.svg) | 阶段 4：总线布线 |
| 早期手绘总图（存档） | [assets/wiring/房车电路.png](./assets/wiring/房车电路.png) | 历史参考 |

> 施工过程照片的拍摄规范（拍什么、怎么拍、放哪里）见 [build-guide.md §6](build-guide.md#_6-施工照片拍摄规范)。

## 子文档

| 文件 | 内容 | 状态 |
|------|------|------|
| [build-guide.md](build-guide.md) | **整车施工主线**：6 阶段步骤、通电顺序、照片规范 | 施工中 |
| [design.md](design.md) | 系统架构：48V 电池、充放电、布线规范 | 设计中 |
| [design-distribution-box.md](design-distribution-box.md) | 中门智能配电箱：48V/12V 配电、继电器、端子排、14 芯线标准 | 设计中 |
| [switch-assignment.md](switch-assignment.md) | 面板开关分配 & IO 通道分配、14 芯线色定义 | 施工中 |
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