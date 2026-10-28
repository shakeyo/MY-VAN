# 外部扩展

涵盖车顶系统和车尾挂载。V80 原厂车顶仅一层铁皮、车尾无扩展接口——通过铝型材平台和拖车杠建立标准化安装基座，所有外部装备模块化挂载、年审可拆。

**核心思路**：平台化安装基座 + 模块化挂载。车顶用 3060 铝型材框架将载荷分散到雨槽和立筋，车尾通过拖车杠方口统一接口挂载储物箱和自行车架。

## 子系统

| 文件 | 内容 | 状态 |
|------|------|------|
| [design-platform.md](design-platform.md) | 3060/3030 铝型材混合框架（车顶平台） | 设计中 |
| [design-solar.md](design-solar.md) | 太阳能板物理安装（电气接入见 [04-power-system](../04-power-system/)） | 设计中 |
| [design-lighting.md](design-lighting.md) | 工作灯、场景灯、示廓灯 | 待设计 |
| [design-storage.md](design-storage.md) | 车顶防水储物箱 | 待设计 |
| [design-spoiler.md](design-spoiler.md) | 前部扰流板降噪 | 待设计 |
| [design-rear-storage.md](design-rear-storage.md) | 车尾储物箱 + 自行车架（拖车杠方口挂载） | 待设计 |
| [design-shower-tent.md](design-shower-tent.md) | 车尾横向淋浴帐（带立腿版，硬地/大风备选） | 设计中 |
| [design-shower-tent-noleg.md](design-shower-tent-noleg.md) | 车尾横向淋浴帐（主推：1000 宽 4 杆 2020 框 + 四面 + 顶 + 前片拉链，无腿；后横杆 1000 整根全水平面折） | 改版设计 |

> 淋浴帐的 **3D 收折动画**：[shower-frame-3d.html](assets/shower-frame-3d.html)（纯 canvas，无需联网，浏览器直接打开；`?t=0` 展开、`?t=1` 收好）。

## 跨模块依赖

- 车顶结构依附 [01-vehicle-layout](../01-vehicle-layout/) 车顶立筋锚固点
- 拖车杠安装见 [00-chassis](../00-chassis/)
- 太阳能电气接入 [04-power-system](../04-power-system/)（MPPT）
- 车顶件颜色与 [03-exterior-appearance](../03-exterior-appearance/) 协调
- 车尾淋浴帐的水/电接口见 [05-water-system](../05-water-system/design.md#未来增项预留-车尾车外淋浴)，帐体防水原则见 [09-shower-module](../09-shower-module/)

## BOM

统一材料清单见 [bom.md](bom.md)。

## 图片

<script setup>
const loaders = Object.values(import.meta.glob('./assets/*.{png,jpg,jpeg,PNG,JPG,JPEG,webp}', { eager: false }))
</script>

<AutoGallery :loaders="loaders" />
