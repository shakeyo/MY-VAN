# 整车布局与结构

总纲模块，定义整车布局方案和基础结构施工。V80 短轴内空约 2.6m×1.75m，需要塞下床、柜、台面、淋浴、设备舱——传统"堆叠式"改装会导致空间压抑且无法年审恢复。本方案采用**三体块分区**（额头段 → 台面段 → 床段），每个体块独立建造、独立拆卸，螺栓压紧地台预埋点而非打胶固定。

**核心思路**：先结构后装饰、每个体块可独立拆卸。铝型材框架替代传统木方龙骨（减重 40%+、可反复拆装不松脱），所有走线走管在框架阶段预埋。

## 子文档

| 文件 | 内容 | 状态 |
|------|------|------|
| [design.md](design.md) | 总体布局设计、三体块方案、关键尺寸 | 设计中 |
| [build-flooring.md](build-flooring.md) | 地板龙骨、XPS 保温、SPC 面层、两侧/吊顶保温隔音 | [x] 已完成 |
| [build-framework.md](build-framework.md) | 铝型材框架体系、模块化连接工艺、驾驶室翻新 | [x] 已完成 |
| [build-windows.md](build-windows.md) | 车窗遮阳帘（磁吸铝箔气泡膜方案） | 已记录 |

## 跨模块引用

- 底盘预处理详见 [00-chassis](../00-chassis/)
- 车顶施工详见 [02-external](../02-external/)
- 电力走线预留见 [04-power-system](../04-power-system/)
- 各体块详细施工见对应模块：07-cabinetry、08-bed-and-seat、09-shower-module

## 图片

<script setup>
const loaders = Object.values(import.meta.glob('./assets/*.{png,jpg,jpeg,PNG,JPG,JPEG,webp}', { eager: false }))
</script>

<AutoGallery :loaders="loaders" />
