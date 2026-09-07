# VAN-PROJECT · Notion 模块镜像铺开清单

> 权力配置：Git 为权威真相源；Notion 镜像层为手机速查。本文记录各模块顶层 doc→Notion 页面映射。
> 执行口径：正文用 Notion 原生块（Heading / 表格保真 / callout / to_do）；配图无上传→以「配图见 git modules/<模块>/…svg|png」文字标注；带 bom 的模块在页内给 bom 概览（04 单独建了 bom 子页）。

## 已镜像完成（全 12 个模块目录已各建子页，挂「VAN 施工手册」下）

| Notion 子页 | 源（git） | 备注 |
|---|---|---|
| 00 · 底盘与车外施工 | `00-chassis/{design,build-chassis,build-rear-mount}.md` | 防锈/装甲/拖车杠 |
| 01 · 整车布局 | `01-vehicle-layout/{design,build-flooring,build-framework,build-windows}.md` | 布局决策+地板/框架/窗 |
| 02 · 车外部件 | `02-external/{design-platform,design-rear-storage,design-solar,...}.md` | 平台/尾箱/太阳能；灯光扰流待设计 |
| 03 · 外观装饰 | `03-exterior-appearance/design.md` | 拉花/贴纸/装饰件 |
| 04 · 电力系统 | `04-power-system/{build-guide,design-distribution-box,switch-assignment}.md` | 施工+箱内+开关通道 |
| └─ 材料清单 bom | `04-power-system/bom.md` | 采购（独立子页） |
| 05 · 用水系统 | `05-water-system/{design,bom}.md` | 清水/灰水/泵/管路；bom 概览在页内 |
| 06 · HVAC 暖通 | `06-hvac/{design,bom}.md` | 驻车空调/柴油暖风/换气/温控风 |
| 07 · 柜体 | `07-cabinetry/{design-countertop,design-overhead,design-bed-cabinet}.md` | 台面/额头柜/床柜 |
| 08 · 床与卡座 | `08-bed-and-seat/{design-bed,design-dinette}.md` | 折叠横床/卡座 |
| 09 · 淋浴模块 | `09-shower-module/{design,bom}.md` | 软隔离防水/年审 |
| 10 · 智能控制 | `10-smart-control/build-guide.md` | 0-9 阶段主线；子模块源索引见页内 callout |
| 11 · 影音娱乐 | `11-entertainment/{design,design-audio}.md` | 投影/显示/音响 DSP |
| 施工进度·任务勾选 TODO | `TODO.md` | 任务状态镜像（回写见 notion-sync.md） |

## 待铺开模块
无（全模块目录均已有 Notion 子页）。

## 尚未做的（可选递补，边际价值低，源已在 git）
- 04 的纯 ASCII 图 / design.md 论证逐条镜像（正文已是建设性摘要）。
- 10 子模块独立页深铺（energy/gateway/media/n100-ha/robot/sensors 的 design/bom）。
- 各 bom 单独子页化（目前 04 独立子页，其余 bom 概览在页内）。
- 后续若 git 新增 build-guide 级执行主文档，再补镜像。

## 铺一个模块的标准动作模板（供未来新增模块用）
1. 源 doc 逐篇 read（含子文件/图清单）；挑 field 有效正文建 Notion 子页。
2. Notion 建子页于「VAN 施工手册」下，命名 `XX · <title>`，标题下 callout 注明 git 源路径。
3. 表格→Notion 保真表格；heading/编号/callout/检查清单→原生块；ASCII/文本图→「配图见 git」文字标注。
4. 有 `bom.md` 则页内给 bom 概览或建独立子页（照 04 样式）。
5. 回读校验再交用户手机验收。
6. 回填本清单「已镜像完成」行，并 commit（notion-sync.md 同步更新映射）。

## 优先级建议
模块已全部铺开；未来重点转向：TODO 状态回写、10 子模块深铺、以及 git 侧新增文档的增量镜像。
