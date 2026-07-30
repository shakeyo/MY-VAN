# PVE 基础环境搭建

## 硬件要求

- **主机**: N100 迷你主机（建议 16GB RAM + 512GB NVMe SSD）
- **供电**: 12V 稳压供电（从副电瓶取电），功耗约 6-15W
- **网络**: 千兆网口接入 GL.iNet 路由器 LAN 口

## 安装 Proxmox VE

### 1. 制作安装 U 盘

下载 [Proxmox VE ISO](https://www.proxmox.com/downloads)（推荐 8.x 版本），使用 balenaEtcher 或 Rufus 写入 U 盘。

### 2. BIOS 设置

N100 主机开机按 Del/F2 进入 BIOS：
- Boot → 选择 UEFI 启动
- Power → 设置为上电自动开机（Power On After Power Loss）
- 关闭 Secure Boot

### 3. 安装 PVE

按照安装向导操作，关键配置：

```
Management IP:  192.168.8.10/24
Gateway:        192.168.8.1
Hostname:       pve.van.local
Disk:           选择 NVMe SSD，ext4 格式
```

安装完成后访问 `https://192.168.8.10:8006`。

### 4. 安装后优化

```bash
# SSH 登录 PVE 主机

# 移除企业源（免费版）
rm /etc/apt/sources.list.d/pve-enterprise.list
echo "deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription" > /etc/apt/sources.list.d/pve-no-subscription.list

# 更新系统
apt update && apt dist-upgrade -y

# 安装常用工具
apt install -y vim curl wget htop iotop net-tools
```

## LXC 容器模板下载

在 PVE Web UI 中，进入 `local` 存储 → `CT Templates` → `Templates`，下载：

- `debian-12-standard` (用作 HA Supervised / Frigate / Mosquitto 的基础)

也可以通过命令行：

```bash
pveam update
pveam download local debian-12-standard_12.0-1_amd64.tar.zst
```

## 存储规划

建议创建以下目录结构：

```
/var/lib/vz/
├── template/cache/     # LXC 模板
├── images/             # VM 磁盘镜像
└── data/               # 共享数据
    ├── ha-config/      # HA 配置持久化
    ├── frigate/        # Frigate 录像存储
    └── media/          # 媒体文件
```

## PVE 网络配置

确认 `/etc/network/interfaces` 网桥配置正确：

```
auto vmbr0
iface vmbr0 inet static
    address 192.168.8.10/24
    gateway 192.168.8.1
    bridge-ports enp1s0
    bridge-stp off
    bridge-fd 0
```

## 下一步

PVE 就绪后，继续部署 [Home Assistant](./home-assistant.md)。
