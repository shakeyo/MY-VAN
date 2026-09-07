# VAN-PROJECT ↔ Notion 同步手册

> Git 是方案正文与任务的**唯一权威唯一真相源**。Notion 是**手机端速查镜像 + 任务勾选前线**。
> 编辑永远发生在 git；本页声明 Notion 每个镜像页的源文件与同步方式，防止两边各写一版。

## 分工总纲

| 内容 | 放哪 | 归属 / 权威 | 电话/现场用途 |
|------|------|------------|--------------|
| 代码(固件/HA配置/React仪表盘/站点) | git | git 唯一 | 不镜像 |
| 模块执行/施工/设计/bom 文档 | git + Notion 镜像 | **git 定稿** | Notion 只读速查 |
| 项目进度/任务 TODO | git TODO.md + Notion 勾选 | **Notion 勾选**，回写 git | 手机上勾/加 |
| 配图 SVG/PNG(施工图) | git diagrams/ | git | Notion 无法上传→以「配图见 git diagrams/*.svg」文字标注 |

## Notion 各页 ↔ git 源映射

镜像层挂在 Notion 页面「VAN 施工手册」下：

| Notion 页 | git 源 | 备注 |
|-----------|--------|------|
| 00 · 底盘与车外施工 | `modules/00-chassis/{design,build-chassis,build-rear-mount}.md` | 防锈/装甲/拖车杠 |
| 01 · 整车布局 | `modules/01-vehicle-layout/{design,build-flooring,build-framework,build-windows}.md` | 布局 + 地板/框架/遮阳 |
| 02 · 车外部件 | `modules/02-external/{design-platform,design-rear-storage,design-solar,...}.md` | 平台/尾箱/太阳能 |
| 03 · 外观装饰 | `modules/03-exterior-appearance/design.md` | 拉花/贴纸/装饰 |
| 04 · 电力系统 | `modules/04-power-system/{build-guide,design-distribution-box,switch-assignment}.md` | 施工+箱内+开关通道 |
| └─ 材料清单 bom | `modules/04-power-system/bom.md` | 采购（独立子页） |
| 05 · 用水系统 | `modules/05-water-system/{design,bom}.md` | 水路+泵+排水 |
| 06 · HVAC 暖通 | `modules/06-hvac/{design,bom}.md` | 空调/暖风/换气/温控风 |
| 07 · 柜体 | `modules/07-cabinetry/{design-countertop,design-overhead,design-bed-cabinet}.md` | 台面/额头柜/床柜 |
| 08 · 床与卡座 | `modules/08-bed-and-seat/{design-bed,design-dinette}.md` | 折叠横床/卡座 |
| 09 · 淋浴模块 | `modules/09-shower-module/{design,bom}.md` | 软隔离防水/年审 |
| 10 · 智能控制 | `modules/10-smart-control/build-guide.md` | 智能控制 0-9 阶段 |
| 11 · 影音娱乐 | `modules/11-entertainment/{design,design-audio}.md` | 投影/显示/音响 DSP |
| 施工进度·任务勾选 TODO | `TODO.md` | 任务状态镜像 |

## 一、任务 TODO 回写流程（Notion → git）

页面「施工进度·任务勾选 TODO」里的每一行 `to_do`，对应 git `TODO.md` 中的一个任务行。

**触发**：用户在手机/电脑 Notion 勾选或新增任务后，对准助手说「同步 TODO」。

**操作步骤（助手执行）**：
1. 从页面读全部 to_do 的 **文本**（注意：当前 dsh `notion_read_page` **不返回 `checked` 布尔**，已实测——因此**不能**仅靠读页拿到用户勾了哪些行）。
2. 由**用户提供的指示**确定实际差异，例如用户在 Notion 勾了几项后说“同步 TODO”，其指示通常包含任务文字或“把 X 标完成”；助手据此读 `TODO.md` 建「任务文字→行号」索引。
3. 计算差异：
   - 用户说完成且 git 行为 `[ ]` → 改 `[x]`
   - 用户取消且 git 行为 `[x]` → 改回 `[ ]`
   - Notion 新增任务行（用户说明）→ 追加到最贴合分类小标题下
4. 用 edit 改 `TODO.md`，仅动有差异的行，不重排版、不动历史无关行。
5. `git add TODO.md && git commit`（提交前让用户知情即可）。

> 备用增强（若日后需读真正的勾选位）：可在创建看板时于每条任务标题加形如 `【done|todo】` 的前缀，把状态编码进文本，使 read_page 能读到——届时自动同步可行。当前未采用，采用“文本+用户指示”方案。

**匹配不唯一的规避**：优先按「同一分类 heading 下、文字近似度最高」定位；若多条同文本，用 `replace_all=false` + 带分类上下文的唯一串。

> 注意：Notion 里正文页(04 等)是 git 文档的只读镜像。**不要再 Notion 改正文**，请只在末尾用「+」加临场注记，正式改回 git 对应 .md，我再整段重推覆写该镜像页子树。

## 二、镜像维护（git → Notion 重推）

当某模块文档在 git 里被改（`git log`/你自己改），要刷新对应 Notion 镜像页：
1. read git 源 md 变化段。
2. **整段重建**对应 Notion 页的核心内容（因加锁正文不可逐块改，用"重建该节/整页子树"策略，git 版恒被写回）。不逐字 diff——以 git 为准冲回，Notion 手动物会丢，故正文镜像视作只读。
3. 建/改前先确认该页未被用户 UI 锁定（锁定后 API 写入会被拦，需用户先解锁再推——由用户手动锁正文）。

## 三、锁定策略（已与用户商定）

- Notion UI 的「锁定」可阻止你我(owner)都无法改——是用户在 UI 手动操作，**不在本工具/API 能力内**。
- 未经锁定正文虽可改，但整体流程以「git 为权威、镜像整段覆写会丢弃 Notion 手改」达成伪锁效果。
- 若你真想把某块不可再动的**定稿**正文永久化，可自行在 UI 锁定该块/页；锁后需要改时先解锁再让我推。

## 四、配图与施工图

dsh/API 无法把本地 SVG/PNG 上传进页面，正文内以「配图见 git `04-power-system/diagrams/xxx.svg`」文字标注，看图需桌面/git。若日后需要，可把关键 SVG 另存为 PNG 手动拖进 Notion(UI) 作为现场对照（不进本自动流程）。

## 五、会话内工作根

- Git 工作区：`/Users/fung/Workspace/VAN-PROJECT`
- 镜像父页：`📐 VAN 施工手册` = page `3d4e2159-512c-81cc-ad90-e1fa2c107c8d`
- 子页：`00·底盘`=`3d4e2159-512c-810c-bc40-ed64296bd1f1`；`01·整车布局`=`3d4e2159-512c-8165-bf23-ce1d562751c2`；`02·车外`=`3d4e2159-512c-816e-8c34-ff9fa287ef2f`；`03·外观`=`3d4e2159-512c-81e9-a902-f91f4e7c5e19`；`04·电力`=`3d4e2159-512c-819f-a321-ded7d846814c`(bom=`3d4e2159-512c-8140-8bf8-f1354c115474`)；`05·用水`=`3d4e2159-512c-819b-97af-e0277daa8c28`；`06·HVAC`=`3d4e2159-512c-81e3-a302-f6d24ea6e3ce`；`07·柜体`=`3d4e2159-512c-81ef-a085-d0d12099fe7f`；`08·床与卡座`=`3d4e2159-512c-8131-a26a-db4a859ba5cb`；`09·淋浴`=`3d4e2159-512c-8119-8886-eda094915052`；`10·智能控制`=`3d4e2159-512c-819e-9491-dc3f82d2289c`；`11·影音`=`3d4e2159-512c-81c4-ba09-ec979ea28d3a`；`TODO看板`=`3d4e2159-512c-813f-b80c-d269059dec91`
- Notion 展示给用户的完整 URL 见各工具返回。

> 追加镜像新模块时，先在「VAN 施工手册」页建对映子页并回填本表“(待铺)”行。勿全量越权覆写其它模块—每批征求用户归属。
