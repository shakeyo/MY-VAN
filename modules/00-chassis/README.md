# 底盘

底盘预处理是整个改装的基础层。V80 原厂底盘只有基础防锈，房车改装需要在底板上开孔走水/电/排风管路，且长期承受水箱、电池、柜体等载荷，因此必须在施工前完成防锈强化、结构加固和隔音隔热。

**核心思路**：先保护、再开孔、最后挂载。所有开孔位置由 [01-vehicle-layout](../01-vehicle-layout/) 的总体布局决定，避免后期返工。

## 子文档

| 文件 | 内容 | 状态 |
|------|------|------|
| [design.md](design.md) | 底盘处理总体规划 | 设计中 |
| [build-chassis.md](build-chassis.md) | 施工指南：装甲喷涂、防锈、开孔加固 | 待施工 |

## 子系统

| 子系统 | 说明 | 状态 |
|--------|------|------|
| 底盘装甲 | 防锈喷涂、底盘护甲 | 待设计 |
| 隔音隔热 | 底盘隔音棉 + 隔热层 | 待设计 |
| 开孔与加固 | 水路/电线/排风底盘开孔，孔位加固密封 | 待设计 |
| 底盘挂载 | 备胎架、水箱挂架等底盘附件 | 待设计 |

## 跨模块依赖

- 先于所有模块：底盘处理是所有后续工程的前提
- 开孔位置由 [01-vehicle-layout](../01-vehicle-layout/) 总体布局决定
- 水箱挂载与 [05-water-system](../05-water-system/) 协同

## 图片

<script setup>
const loaders = Object.values(import.meta.glob('./assets/*.{png,jpg,jpeg,PNG,JPG,JPEG,webp}', { eager: false }))
</script>

<AutoGallery :loaders="loaders" />
