# 车机面板部署

车机面板是一个**自包含的深蓝 UI**（仿原 React 仪表盘主题），**由 ESP32 自己托管**，手机/安卓车机打开即用，完全离线，不依赖 N100 / HA / 外网。

- 面板本体：`modules/10-smart-control/gateway/esphome/web/index.html`（原生 HTML/CSS/JS，零依赖）
- 数据来源：ESPHome 原生 REST（开关 `/switch/<name>`、光伏 `/sensor/<name>`、场景档位）
- 机制详见：[gateway/esphome/README.md](../../modules/10-smart-control/gateway/esphome/README.md)「手机控制面板」小节

> 原 `rv-smart-dashboard`（React + Vite，部署在 N100/Nginx）已废弃并删除，由 ESP32 自托管面板取代。

## 部署位置

| 设备 | 位置 | 用途 |
|------|------|------|
| 安卓车机 / 手机 | 生活区壁挂 + 随身 | 主控面板，Fully Kiosk 全屏锁定（车机） |
| 兜底热点 | ESP32 自身 AP（`FORAGER-GATEWAY`） | 无路由器时手机直连 `192.168.4.1` |

## 访问入口

```
http://<esp32-ip>/dashboard          # 主用（车内 192.168.10.20 或家里 DHCP 地址）
http://192.168.4.1/dashboard         # 兜底 AP（连 ESP32 热点 FORAGER-GATEWAY 后）
```

原生 ESPHome web_server 前端仍在 `/`（调试/OTA 用），两者并存互不干扰。

## 烧录与更新

面板页面是打进固件 Flash 的，改界面后必须**重新编译 + 烧录**才生效：

```bash
cd modules/10-smart-control/gateway/esphome
esphome run prod.yaml                # 编译 + USB 烧录 + 进日志（首次需 USB）
# 或 OTA（设备同网段时）：
esphome upload prod.yaml --device myvan-485-gateway.local
```

详见 [build-guide.md §6.5](../../modules/10-smart-control/gateway/build-guide.md)。

## 车机 Fuly Kiosk 配置（安卓车机，可选）

1. 安装 Fully Kiosk Browser
2. 起始 URL 设为 `http://<esp32-ip>/dashboard`
3. 启用 Kiosk 模式（全屏 + 隐藏导航栏）
4. 屏幕常亮（仅充电时）、运动检测唤醒（靠近自动亮屏）

> 面板是**移动端优先**布局，手机浏览器直接打开即可获得最佳观感；无需 HA / Nginx 中转。
