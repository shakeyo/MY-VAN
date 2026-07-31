# 床铺与座椅

后横床与折叠卡座。后横床的核心矛盾：1.35m 宽床面 + 过道无法在 1.75m 内宽中同时存在。解决方式是翻折床——两块 9mm 海洋板平时垂直贴墙（左板为床侧立板，右板为柜侧下翻门），睡觉时翻平对接。立柱内退 40mm + 板子外凸 40mm，机构完全隐藏，气弹簧辅助单人操作。

**核心思路**：空间分时复用。白天是过道和柜门，晚上是 1.35m 整床。折叠卡座同理——用餐时展开，行车时收起，集成冰箱节省独立冰箱位。

## 子系统

| 文件 | 内容 | 状态 |
|------|------|------|
| [design-bed.md](design-bed.md) | 后横床（固定基座 + 抽拉机构） | 待设计 |
| [design-dinette.md](design-dinette.md) | 折叠卡座（铝型材框架 + 冰箱集成） | 设计中 |

## 跨模块依赖

- 床基座高度 = [07-cabinetry](../07-cabinetry/) 床段柜顶高度（需等高）
- 基座锚固点由 01-vehicle-layout 预埋
- 卡座框架锚固于原车座椅滑轨或预埋木方

## BOM

统一材料清单见 [bom.md](bom.md)。

## 图片

<script setup>
const loaders = Object.values(import.meta.glob('./assets/*.{png,jpg,jpeg,PNG,JPG,JPEG,webp}', { eager: false }))
</script>

<AutoGallery :loaders="loaders" />
