# 仪表盘部署

rv-smart-dashboard 是配套的 React 前端仪表盘，部署在安卓车机或平板上，通过 HA WebSocket API 实时展示车况。

## 部署位置

| 设备 | 位置 | 用途 |
|------|------|------|
| 安卓车机 (10-13") | 生活区壁挂 | 主控面板，Fully Kiosk 全屏锁定 |
| 手机/平板 | 移动使用 | 随时查看、控制 |

## 方式一：安卓车机部署（推荐）

### 步骤

```bash
# 1. 在开发机器上构建生产版本
cd software/rv-smart-dashboard
pnpm install
pnpm build

# 2. 上传到 N100 的 Web 服务目录
scp -r dist/* root@192.168.8.10:/var/www/dashboard/

# 3. 在 N100 上安装 Nginx
apt install -y nginx
```

Nginx 配置 `/etc/nginx/sites-available/dashboard`：

```nginx
server {
    listen 8080;
    server_name _;
    root /var/www/dashboard;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # 代理 HA API（避免跨域问题）
    location /api/ha/ {
        proxy_pass http://192.168.8.11:8123/api/;
        proxy_set_header Host $host;
        proxy_set_header Authorization $http_authorization;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### 车机访问

在安卓车机浏览器中打开：`http://192.168.8.10:8080`

安装 Fully Kiosk Browser 锁定到此页面即可。

## 方式二：开发环境

在笔记本上开发调试：

```bash
cd software/rv-smart-dashboard
pnpm install
pnpm dev
# 访问 http://localhost:5173
```

配合 [dev-environment 开发环境](../../software/dev-environment/) 可以模拟完整的 HA 后端。

## 环境变量配置

生产构建时，设置 HA 连接信息：

```bash
# .env.production
VITE_HA_URL=http://192.168.8.11:8123
VITE_HA_TOKEN=your_long_lived_access_token
```

在 HA 中创建长期访问令牌：`个人设置` → `长期访问令牌` → `创建令牌`

## 安卓车机 Fully Kiosk 配置

1. 安装 Fully Kiosk Browser
2. 设置起始 URL：`http://192.168.8.10:8080`
3. 启用 Kiosk 模式（全屏 + 隐藏导航栏）
4. 设置屏幕常亮（仅充电时）
5. 启用运动检测唤醒（靠近自动亮屏）
6. 配置 MQTT（可选，用于 HA 远程控制车机屏幕）

## 更新部署

```bash
#!/bin/bash
# deploy.sh — 一键部署脚本
cd software/rv-smart-dashboard
pnpm build
rsync -avz --delete dist/ root@192.168.8.10:/var/www/dashboard/
echo "部署完成，访问 http://192.168.8.10:8080"
```
