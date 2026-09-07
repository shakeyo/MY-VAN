# VAN-PROJECT · Notion 模块镜像铺开清单

> 权力配置：Git 为权威真相源；Notion 镜像层为手机速查。本文列"待铺开模块"的源 doc→Notion 页面映射，方便有真人选出模块后近机械式执行。**一个模块铺开前先经用户确认**，母页固定为「VAN 施工手册」。
> 执行口径：正文用 Notion 原生块（Heading / 表格保真 / callout / 编注 / to_do 检查表）；配图无上传→以「配图见 git modules/<模块>/…svg|png」文字标注；每模块在其自身子页下可再放 bom 子页。

## 已镜像完成
| Notion 子页 | 源（git） |
|---|---|
| 04 · 电力系统 | `modules/04-power-system/{build-guide,design-distribution-box,switch-assignment}.md` |
| └─ 材料清单 bom | `modules/04-power-system/bom.md` |
| 10 · 智能控制 | `modules/10-smart-control/build-guide.md`（阶段0-9+拍摄+扩展）；子模块(energy/gateway/media/n100-ha/robot/sensors)以源索引 callout 呈现，深铺另开子页 |
| 01 · 整车布局 | `modules/01-vehicle-layout/{design,build-flooring,build-framework,build-windows}.md` | design决策+地板/框架/窗 |
| 施工进度·任务勾选 TODO | `TODO.md`（回写流程另见 notion-sync.md） |

## 待铺开模块（按源 md 存在度高→低排序，便于挑重点先做）

| # | 模块目录（git） | 推荐源 doc（顶层 md） | 附 bom? |
|---|---|---|---|
| 00 | `00-chassis` 底盘 | `build-chassis.md`,`build-rear-mount.md`,`design.md` | 无 |
| 02 | `02-external` 外部（太阳能/平台/照明/后仓） | `design-*.md` 组（platform/rear-storage/solar/lighting/storage/spoiler） | `bom.md` |
| 05 | `05-water-system` 水路 | `design.md`,`build-guide?`（仅顶层有 design.md+bom.md） | `bom.md` |
| 06 | `06-hvac` 空调暖风 | `design.md` | `bom.md` |
| 07 | `07-cabinetry` 柜体 | `design-countertop.md`,`design-overhead.md`,`design-bed-cabinet.md` | `bom.md` |
| 08 | `08-bed-and-seat` 床与卡座 | `design-bed.md`,`design-dinette.md` | `bom.md` |
| 09 | `09-shower-module` 淋浴 | `design.md` | `bom.md` |
| 11 | `11-entertainment` 影音 | `design-audio.md`,`design.md` | 无 |
| 03 | `03-exterior-appearance` 外观 | `design.md` | 无 |

## 铺一个模块的标准动作模板
1. 源 doc 逐篇 read（含子文件/图清单）；挑 field 有效正文建 Notion 子页。
2. Notion 建子页于「VAN 施工手册」下，命名 `XX · <title>`，标题下 callout 注明 git 源路径。
3. 表格→Notion 保真表格；heading/编号/callout/检查清单→原生块；ASCII/文本图→「配图见 git」文字标注（不逐行输入）。
4. 有 `bom.md` 则建其下 `材料清单 bom` 子页照 04 样式。
5. 回读校验再交用户手机验收。
6. 回填本清单“已镜像完成”行，并 commit 到 git（notion-sync.md 同步更新映射）。

## 优先级建议
用户若一次只挑一个：首推 `10-smart-control`（内容厚、现场调试依赖强）或 `01-vehicle-layout` 施工主线；其次带 bom 的水/暖/卫近采购对照。
