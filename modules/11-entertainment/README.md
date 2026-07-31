# 影音娱乐

全车影音系统，覆盖视觉（投影+显示器）和听觉（8 通道 DSP 音响）两条线。投影用于驻车观影，显示器用于日常使用，音响兼顾行车导航和驻车娱乐。整套系统以 [10-smart-control](../10-smart-control/) 的 N100 主机为算力核心，HDMI 输出到显示设备，音频经 DSP 功放驱动全车 8 只喇叭。

**核心思路**：一机多用。N100 既是 Home Assistant 中枢，也是影音播放器。音源三路混入 DSP（N100 AUX + 车载导航 + 蓝牙），蓝牙通道覆盖手机和投影仪无线连接场景。

## 子文档

| 文件 | 内容 | 状态 |
|------|------|------|
| [design.md](design.md) | 投影幕布、投影仪、显示器、键鼠收纳 | 设计中 |
| [design-audio.md](design-audio.md) | 全车音响：Alpine R600 DSP 功放 + 8 通道主动分频 | 设计中 |

## 子系统

| 子系统 | 说明 | 状态 |
|--------|------|------|
| 投影幕布 | 卷轴式，中部安装，幕布降落不挡过道 | 待设计 |
| 投影仪 | 车尾快装支架，HDMI + USB 供电 | 待设计 |
| 显示器 | 右侧台面靠尾门，支架可折叠贴墙 | 待设计 |
| 全车音响 | Alpine R600 8ch DSP 主动分频，6 喇叭 + 低音炮 | 设计中 |
| 操作输入 | 无线键鼠 + 收纳，投影遥控 | 待设计 |

## 跨模块依赖

- N100 主机由 [10-smart-control](../10-smart-control/) 提供
- 额头柜喇叭安装位由 [07-cabinetry](../07-cabinetry/) 提供
- 投影仪/显示器 HDMI 线需在吊顶和侧壁预埋，与 [01-vehicle-layout](../01-vehicle-layout/) 协同
- DSP 功放 12V 供电来自额头柜配电箱或 [04-power-system](../04-power-system/)

## 图片

<script setup>
const loaders = Object.values(import.meta.glob('./assets/*.{png,jpg,jpeg,PNG,JPG,JPEG,webp}', { eager: false }))
</script>

<AutoGallery :loaders="loaders" />
