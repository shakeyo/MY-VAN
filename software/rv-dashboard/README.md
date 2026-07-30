# rv-smart-dashboard — 房车智能仪表盘

基于 React + TypeScript + Vite 的房车中控仪表盘，通过 Home Assistant WebSocket API 实现全车设备监控与场景切换。

## 功能

- **电力监控** — 48V/12V 双系统电量、充放电功率、库仑计数据实时展示
- **水位监测** — 净水箱、灰水箱水位百分比与趋势图
- **场景模式** — 驾驶模式 / 影院模式 / 营地模式一键切换
- **设备控制** — 灯光、水泵、排风扇的开关与状态反馈
- **快捷面板** — 底部常驻导航，支持常用开关一键操作

## 技术栈

| 类别 | 方案 |
|------|------|
| 框架 | React 18 + TypeScript |
| 构建 | Vite 6 |
| 样式 | Tailwind CSS 3 |
| 状态管理 | Zustand |
| 图表 | Recharts |
| UI 组件 | Radix UI + shadcn/ui |
| 后端通信 | Home Assistant WebSocket API |

## 开发

```bash
# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 构建生产版本
pnpm build

# 预览构建产物
pnpm preview
```

## 与 Home Assistant 集成

仪表盘通过 HA WebSocket API (`src/services/haApi.ts`) 与 Home Assistant 通信：

- 实时订阅实体状态变更
- 调用 `callService` 执行开关、场景切换等操作
- 所有设备控制逻辑在 HA 侧完成，仪表盘仅做展示与指令发送

确保 HA 实例在同一局域网内，且已启用 WebSocket API。
