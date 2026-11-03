# 控制面板换肤（Theme）设计

> 适用范围：[`web/panel-dot.html`](../../modules/10-smart-control/gateway/esphome/web/panel-dot.html) —— ESP32 自托管的手机控制面板。
> 目标：**换一套皮肤 = 只改 CSS 变量，不改任何组件规则、不碰数据层。**

---

## 1. 为什么这么设计

面板是一个 **单文件、gzip 后打进 Flash、完全离线** 的页面。这带来三个硬约束：

| 约束 | 影响 |
|---|---|
| 单文件进 Flash | 不能引入外部主题 CSS/JS，皮肤必须写在同一文件里 |
| gzip 后体积有限 | 皮肤必须是"纯变量覆盖"，不能复制整套组件样式 |
| 离线 | 不能用 CDN 字体，字体必须内嵌（见 §5） |

所以方案是**单层 CSS 自定义属性契约**：组件样式只写一次、只消费 token；每款皮肤只是一组 `--token: value` 覆盖。

---

## 2. Token 契约

全部 token 定义在 `<style>` 顶部的 `:root`，按 8 类分组。**组件规则里不允许出现写死的颜色/圆角/字体**。

### 2.1 字体族

| Token | 说明 |
|---|---|
| `--font-body` | 正文、按钮、格子标签 |
| `--font-num` | 数值、大写字、时钟（点阵大数字） |
| `--font-mono` | 仅日志区（时间戳/十六进制需要等宽对齐） |

### 2.2 表面与文字（按层级由底到顶）

| Token | 用在哪 | paper 默认 |
|---|---|---|
| `--c-page-bg` | 手机壳之外的页面底色 | `#EDEDEB` |
| `--c-shell` | 顶栏 / 底栏 | `#FAFAF8` |
| `--c-card` | 卡片 | `#FFFFFF` |
| `--c-sunken` | 卡片内的凹槽块（`.stat` / 单体格 / 皮肤按钮） | `#EDEDEB` |
| `--c-raised` | 选中态块 / 进度槽 | `#E4E4E1` |
| `--c-text` | 主文字、图标 | `#2B2B2B` |
| `--c-text-2` | 次级文字 | `#6E6E6B` |
| `--c-text-3` | 弱化文字 / 提示 | `#9C9C98` |
| `--c-line` | 卡片描边、分隔线 | `#D7D7D3` |
| `--c-line-2` | 更重的描边 | `#C4C4BF` |

### 2.3 语义色

**语义不随皮肤改变**：`ok` 永远是"正常"，`danger` 永远是"异常"。皮肤只换色相，不换含义。

| Token | 含义 | paper 默认 |
|---|---|---|
| `--c-accent` | 主强调：激活 / 选中 / 导航下划线 | `#C4262E` |
| `--c-info` | 信息：联网、焦点环 | `#2C6E8F` |
| `--c-ok` | 正常 / 充电中 / 电量充足 | `#2F7A4D` |
| `--c-warn` | 警告 / 压差偏高 / 电量偏低 | `#A8730F` |
| `--c-danger` | 异常 / 告警 / 电量告急 | `#C4262E` |
| `--c-ok-bg` `--c-warn-bg` `--c-danger-bg` | badge 浅底，用 `color-mix` 自动派生 | — |

> 电量环的三档配色由 JS 读 `--c-ok / --c-warn / --c-danger`，改皮肤这圈颜色自动跟着变。

### 2.4 控件

| Token | 说明 |
|---|---|
| `--c-switch-off` / `--c-switch-on` / `--c-knob` | 开关轨道与旋钮 |
| `--c-slider` | 滑块强调色 |
| `--c-mark-on` | 开关格下方小圆点（开启态） |
| `--c-scene-on` | 情景卡激活描边 |

### 2.5 形状

| Token | 说明 |
|---|---|
| `--r-card` / `--r-block` / `--r-chip` / `--r-pill` | 圆角四档 |
| `--bd-card` / `--bd-card-on` | 卡片描边（可改成 2px 做高对比） |
| `--shadow-card` / `--shadow-knob` | 阴影 |
| `--glow-accent` / `--glow-text` | **激活态柔光**。取自 `design/cabin-climate.html` 的 `0 0 22px -10px`（负扩散，可见光晕仅约 12px） |
| `--glow-tile` | 密集网格（开关格）专用、更收敛的柔光。格子间隔只有 8px，照搬 22px 会串色 |

> **视觉基准**：排版与装饰细节以 [`design/cabin-climate.html`](cabin-climate.html) 为准 ——
> 卡片内边距 `16px 16px 18px`（`--pad-card`）、激活柔光、图标描边 1.4、
> 区块标题 17px/500 的字重与间距、雪花等图标用「6 主轴 + 12 斜枝」的精细版本。
>
> **激活态的正确做法**（照设计稿）：**底色不换**，只让描边变强调色 + 图标变强调色 +
> 描边外侧一抹负扩散柔光。不要用灰色底填充整块——那是错的视觉重心。
> 设计稿里只有 `.mode.heating.on` 用了一层极淡的 `linear-gradient(180deg, rgba(43,43,43,.05), transparent 70%)`。

### 2.6 排版

`--fs-sec` `--fs-label` `--fs-body` `--fs-val` `--fs-num` `--fs-clock` `--fs-nav` `--fs-log` `--lh-tight` `--lh-body`

间距：`--pad-card`（卡片内边距）、`--pad-block`（卡片内小块）、`--gap-card`（卡片间距）。

### 2.7 图标

| Token | 说明 |
|---|---|
| `--icon-size` / `--icon-nav` | 图标尺寸 |
| `--icon-stroke` | **SVG 描边宽度**（JS 在切皮肤时写回每个 `<svg>`）。默认 1.5，高对比皮肤 2.1 |
| `--icon-off-opacity` | 关闭态图标透明度 |

### 2.8 装饰

| Token | 说明 |
|---|---|
| `--deco-dotword-opacity` | 点阵大字透明度 |
| `--deco-focus` | 键盘焦点环 |
| `--deco-sec-bar` | 区块标题左侧竖条 |

---

## 3. 内置皮肤

| id | 名称 | 定位 |
|---|---|---|
| `paper` | Paper | **默认**。参考图原味：暖白 + 点阵 + 红点缀 |
| `night` | Night | 深色，夜间行车/露营不刺眼 |
| `terminal` | Terminal | 绿字等宽 + 直角，极客/调试风 |
| `contrast` | Contrast | 纯黑白 + 2px 描边 + 粗图标，户外强光可读 |
| `sand` | Sand | **淡黄车漆**，呼应车身漆面。要点：卡片用**纯白**、页面用淡黄，把层次拉开 |
| `neon` | Neon | **未来感**：深空底 + 电光青，激活态青色发光而非红色 |

切换方式：设置页 →「外观 / 皮肤」，选择存 `localStorage['forager_skin']`。

### 设计教训：浅色皮肤别把明度做平

`sand` 初版 page 与 card 都是米黄（`#EAE0D2` → `#FBF6EC`），明度差只有约 8%，
整屏糊成一片、看着发闷。修正版把**卡片拉成纯白 `#FFFFFF`**，页面才保留淡黄，
层次立刻出来。同理，强调色要在白底上够深（`#B07C1A` 而非 `#B4562A`）才够读。

---

## 4. 新增一款皮肤

**只需 3 步，不用改组件规则：**

1. 在 `<style>` 的皮肤区加一段覆盖：

```css
[data-skin="ocean"]{
  --c-page-bg:#0A1620; --c-shell:#0E1E2A; --c-card:#12293A;
  --c-sunken:#173245;  --c-raised:#1D3D53;
  --c-text:#DCEEF7;    --c-text-2:#8FB3C7; --c-text-3:#5F8199;
  --c-line:#1E4055;    --c-line-2:#2A5A75;
  --c-accent:#4FC3F7;  --c-info:#4FC3F7;
  --c-ok:#5FD08A; --c-warn:#F0B94B; --c-danger:#FF6B6B;
  --c-switch-off:#22455C; --c-switch-on:#4FC3F7; --c-knob:#DCEEF7;
  --c-slider:#4FC3F7; --c-mark-on:#4FC3F7; --c-scene-on:#DCEEF7;
  --deco-sec-bar:var(--c-text-2);
  --deco-focus:var(--c-info);
}
```

2. 在 JS 的 `SKINS` 注册表加一行（`id` 必须与 CSS 选择器一致）：

```js
{ id:'ocean', name:'Ocean', note:'深海蓝' },
```

3. 在 `SKIN_SWATCH` 加缩略图配色（底 / 卡片 / 强调）：

```js
ocean: ['#0A1620','#12293A','#4FC3F7'],
```

> 只覆盖**真正需要变**的 token，其余自动继承 `:root` 默认值。

---

## 5. 字体

像素字体无法从 CDN 加载（离线），因此以 `@font-face` + `data:font/woff2;base64` 内嵌：

| 字体 | 用途 | 大小 |
|---|---|---|
| Pixelify Sans | `--font-body` | 7.6 KB |
| Silkscreen 400/700 | `--font-num` | 3.5 + 3.2 KB |

合计约 **14 KB（gzip 后）**，是页面体积的主要构成。

**如果要换字体**：替换对应 `@font-face` 的 base64，或让某款皮肤改 `--font-body` 指向另一族。中文没有像素字形，统一由 `PingFang SC / Microsoft YaHei` 兜底。

---

## 6. 换肤时的附属动作

`applySkin(id)` 除了切 `data-skin`，还会同步：

1. **`meta[theme-color]`** —— 手机浏览器状态栏/地址栏跟着变色
2. **每个 SVG 的 `stroke-width`** —— 高对比皮肤需要更粗的线条
3. **重渲染选择器** —— 更新 `aria-pressed` 与标题旁当前皮肤名

**防闪白**：`<head>` 里有一段内联脚本，在样式生效前就把 `localStorage` 里的皮肤贴到 `<html data-skin>`，避免先画一帧 paper 再跳变。

---

## 7. 不变的部分（刻意的）

皮肤**不改变**以下行为，这是安全底线：

- 实体映射表（`ENTITIES` / `SENSORS` / `BMS_*` …）与 yaml 的对应关系
- SSE `/events` 订阅与 REST 命令通道
- 页面结构、导航层级、触控尺寸（≥44px）
- 未上线/离线降级逻辑（`--`、虚线占位、数据龄）
- 语义色含义（ok 永远是好，danger 永远是坏）

---

## 8. 体积代价

| 版本 | gzip |
|---|---|
| 深蓝版 `index.html` | 24.0 KB |
| 点阵版（单皮肤，无换肤） | 34.1 KB |
| 点阵版 + 5 套皮肤 | 38.5 KB |

多出的约 4.4 KB 主要是皮肤 CSS 与选择器 UI。相对主网关 53% 的 Flash 占用，这点增量可接受。
