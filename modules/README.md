# 模块索引

本项目按**功能模块**组织，每个模块自包含设计决策、施工指导和材料清单。

## 模块列表

| 编号 | 模块 | 设计决策 | 施工指导 | 材料清单 | 状态 |
|------|------|----------|----------|----------|------|
| 00 | [整车布局与结构](./00-vehicle-layout/) | — | [build-guide.md](./00-vehicle-layout/build-guide.md) | — | 进行中 |
| 01 | [电力系统](./01-power-system/) | [design.md](./01-power-system/design.md) | — | [bom.md](./01-power-system/bom.md) | 进行中 |
| 02 | [智能控制系统](./02-smart-control/) | [design.md](./02-smart-control/design.md) | — | [bom.md](./02-smart-control/bom.md) | 进行中 |
| 03 | [用水系统](./03-water-system/) | — | — | [bom.md](./03-water-system/bom.md) | 待启动 |
| 04 | [淋浴模块](./04-shower-module/) | [design.md](./04-shower-module/design.md) | — | [bom.md](./04-shower-module/bom.md) | 待启动 |
| 05 | [折叠卡座](./05-foldable-seat/) | [design.md](./05-foldable-seat/design.md) | — | [bom.md](./05-foldable-seat/bom.md) | 待启动 |
| 06 | [车顶平台与太阳能](./06-roof-platform/) | [design.md](./06-roof-platform/design.md) | — | [bom.md](./06-roof-platform/bom.md) | 待启动 |
| 07 | [额头柜](./07-overhead-cabinet/) | [design.md](./07-overhead-cabinet/design.md) | — | [bom.md](./07-overhead-cabinet/bom.md) | 待启动 |
| 08 | [HVAC 系统](./08-hvac/) | — | — | [bom.md](./08-hvac/bom.md) | 待启动 |

## 使用方式

施工时按模块推进，每个模块内部包含：

- **design.md** — 方案决策、选型依据、关键尺寸
- **build-guide.md** — 施工步骤、工艺要点、检查清单、问题记录
- **bom.md** — 材料清单（器件型号、数量、购买链接）
- **assets/** — 图纸、模型、过程照片、实测数据

## 跨模块依赖

```
00-vehicle-layout (布局/保温/框架)
    ├── 01-power-system (电力)
    ├── 02-smart-control (智能)
    ├── 03-water-system (水路)
    ├── 06-roof-platform (车顶)
    └── 07-overhead-cabinet (额头柜)

01-power-system
    └── 02-smart-control (依赖电力系统的常电干线)

03-water-system
    └── 04-shower-module (淋浴依赖总水路)
```
