# 命名方案（SSOT）

本文件是这台车的**命名唯一事实来源**。所有代码、配置、文档、车身字均以此为准。

## 定稿

```
车名        FORAGER · 觅食者号
车尾字      UMAMI
系统前缀    palate.
行程模块    TASTING ROUTE / 品鉴路线
目的地标签  BAZAAR / FARM / ROADSIDE
内容笔记    terroir/<地区>.md
对外叙事    Flavor Explorer
```

## 分层理由

命名的难点不在选词，而在**分清层级**。同一个词在不同层级承担不同职责，强行合成一个名字必然是平庸的。

### 层级 1｜车辆本名 —— FORAGER

七个候选里唯一**动词性**的词。其余都是名词：BAZAAR 是地方、TERROIR 是概念、PALATE 是器官、UMAMI 是味道——它们都是"探索的对象"。只有 FORAGER 是"**做这件事的人**"。

车是伙伴，应与主人同为动作主体。且 `forage` 自带完整能力描述：**主动寻找、就地取材、不依赖供给**——与 48V 离网、自持生存、模块化可拆的工程哲学同构。

- 中文名：**觅食者号**（"号"字收尾，船名式命名惯例）
- 用法：车尾贴字、README 首句、对外的"我的车叫什么"

### 层级 2｜系统命名空间 —— PALATE

```yaml
# HA 实体前缀（未来新增实体统一使用）
palate.light.kitchen
palate.sensor.fresh_water
palate.sensor.battery_voltage
```

理由：`palate.` 短、无歧义、全小写排版干净。对比：
- `umami.light.kitchen` → 易被误认为灯具品牌
- `terroir.sensor` → 过长，输入成本高
- `forager.light` → 与车辆本名重复，且实体前缀不需要"人设"，只需要"短"

> **注意**：现有 HA 实体已按 `van_mode` / `audio_mode` 等命名，**不强制批量改名**。改名会造成所有自动化引用失效。本节仅约束**新增实体的前缀规则**。若要统一，需同步改 `automations.yaml`、`scene`、`script`。

### 层级 3｜功能与行程（可无限扩展）

| 名称 | 用途 | 示例 |
|------|------|------|
| **TASTING ROUTE** | dashboard 行程模块 | `Route 001 · 潮汕`、`Route 002 · 川西` |
| **BAZAAR** | 目的地类型标签：集市 | `bazaar: 汕头·龙眼市场` |
| **FARM** | 目的地类型标签：农场 | `farm: 大理·某有机农场` |
| **ROADSIDE** | 目的地类型标签：路边摊 | `roadside: G318 服务区` |
| **TERROIR** | 内容层，风物笔记 | `terroir/chaoshan.md` |
| **UMAMI** | 视觉资产：logo、贴纸、车尾字 | —— |
| **Flavor Explorer** | 对外项目叙事（副标题） | —— |

## 一句话记忆

> **FORAGER 是它叫什么，PALATE 是它在系统里怎么被称呼，TASTING ROUTE 是它去哪，UMAMI 是它长什么样。**

## 落地清单

| 位置 | 改动 | 状态 |
|------|------|------|
| `software/home-assistant-config/configuration.yaml` | `homeassistant.name` → `FORAGER` | ✅ |
| `modules/10-smart-control/gateway/esphome/web/index.html` | 品牌字 → `FORAGER` / `FG` logo | ✅ |
| `modules/10-smart-control/gateway/esphome/web/index.html` | `<title>` → `FORAGER · 觅食者号` | ✅ |
| `README.md` | 首句增加车名与 Flavor Explorer 叙事 | ✅ |
| `site/.vitepress/config.mts` | 站点标题（如需要） | ⬜ 待议 |
| 车尾字 / 车牌框 | 物理落地：`UMAMI` | ⬜ 物理施工 |

## 未来可做（名字 → 产品需求）

**TASTING ROUTE 模块**：车上有 GPS（或 Tailscale 定位）+ 时间轴 + Frigate 视觉记录，完全具备自动打点的数据基础。

```
GPS 停留点 → 判定为"到访" → 打标签（bazaar/farm/roadside）→ 生成 Route
```

这不是纯命名游戏——名字定下来，就是一条清晰的开发需求。
