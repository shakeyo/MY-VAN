#!/usr/bin/env python3
"""
本地预览服务器（无 ESP32 时打磨面板用）

模拟 ESP32 web_server 的两条通道，让 web/index.html 在笔记本上跑起来：
  GET  /dashboard  → 直接返回 web/index.html（等同 forager_panel 组件）
  GET  /events     → SSE 流：state / state_detail_all / log / ping
  POST /<domain>/<name>/<action>  → REST 命令，回显并回推 state（模拟继电器动作）

⚠ 这是**开发工具，不随固件发布**，也不参与构建。
   实体名 / 数值全部是假数据，仅用于验证布局、交互与渲染逻辑。

用法：
    cd modules/10-smart-control/gateway/esphome/web
    python3 dev-preview.py            # 然后浏览器打开 http://127.0.0.1:8321/dashboard

参数：
    --port 8321     监听端口
    --no-coulomb    模拟「库仑计未上线」（验证 --占位与未上线提示条）
    --scene N       指定场景页初始档位（0/1/2），默认 0
"""

import argparse
import json
import math
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

WEB_DIR = Path(__file__).resolve().parent
INDEX = WEB_DIR / "index.html"

# ── 实体名必须与各 yaml 的 name: 完全一致（同 index.html 的 ENTITIES 等映射） ──
SWITCH_NAMES = {
    "[中8.Y1] 主灯": False,
    "[中8.Y2] 氛围灯": False,
    "[中8.Y6] 冰箱": False,
    "[中8.Y7] 车尾灯": False,
    "[驾驶室A.Y1] 前射灯": False,
    "[驾驶室A.Y3] 户外灯": False,
    "[驾驶室A.Y2] DSP": False,
    "[驾驶室A.Y4] 副驾排气扇": False,
    "[中4.Y1] 上水泵": False,
    "[中4.Y2] 电控水阀": False,
    "[中4.Y3] 后窗排气扇": False,
}

MPPT_SWITCH_NAMES = {
    "SolarCharge 充电输出": True,
    "SolarEnable 允许充电": True,
}

# 只读传感器：值为 float（number 域用 value 字段）
SENSOR_VALUES = {
    "SolarPV PV电压": 38.4,
    "SolarBat 电池电压": 52.6,
    "SolarChg 充电电流": 12.4,
    "SolarPower 发电功率": 652.0,
    "SolarDay 日发电量": 1840.0,
    "SolarTotal 总发电量": 92500.0,
    "SolarTemp 控制器温度": 34.2,
    "SolarBatTemp 电池温度": 28.7,
    # 库仑计（--no-coulomb 时统统不推，验证未上线态）
    "CoulombSOC 电量百分比": 78.0,
    "CoulombVolt 电池电压": 52.71,
    "CoulombCap 剩余容量": 156.4,
    "CoulombCurr 电流": 6.32,
    "CoulombTime 剩余时间": 24750.0,
    "CoulombPow 功率": 332.9,
    "CoulombDiag 有效帧数": 1284.0,
    "CoulombBad 校验错帧数": 3.0,
    # 场景档位（scene-state.yaml）
    "SceneLight 灯光模式": 1.0,
    "SceneCamp 离车驻车": 0.0,
    "SceneFan 排气扇": 0.0,
    # 系统
    "SysWifi 信号": -58.0,
}

TEXT_NAMES = {
    "SolarState 充电状态": "MPPT充电中",
    "SolarAlert 告警": "无告警",
    "SysWifi SSID": "ooxx",
    "SysWifi IP地址": "192.168.5.6",
}

NUMBER_NAMES = {"SolarLimit 充电限流": 30.0}
BUTTON_NAMES = [
    "SolarA 设为远程控制",
    "SolarB 时钟同步",
    "SolarC 读设置参数",
    "SolarD 蜂鸣器消音",
    "SysRestart 重启设备",
]

# 共享可变状态（命令会改它，SSE 线程读它）
lock = threading.Lock()
state = {
    "switches": dict(SWITCH_NAMES),
    "mppt": dict(MPPT_SWITCH_NAMES),
    "sensors": dict(SENSOR_VALUES),
    "texts": dict(TEXT_NAMES),
    "numbers": dict(NUMBER_NAMES),
}
boot_time = time.time()
LOG_LINES = []
log_sent = [0]      # 已推送到各客户端的日志下标（分连接独立更准确，这里简化为全局）


def log(msg):
    ts = time.strftime("%H:%M:%S")
    LOG_LINES.append(f"[{ts}][I][preview:001]: {msg}")
    del LOG_LINES[:-200]


# ── SSE 事件构造 ──
def ev(event, payload):
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n".encode()


def entity_id(domain, name):
    # 模拟 web_server 的 name_id 格式 domain/<name>
    return f"{domain}/{name}"


def state_event(domain, name, value, is_text=False):
    return ev("state", {
        "name_id": entity_id(domain, name),
        "name": name,
        "domain": domain,
        "value": value,
        "state": value if is_text else ("ON" if value else "OFF") if domain == "switch" else str(value),
    })


def full_snapshot():
    """初次连接时把全部实体推一遍，等价于 ESPHome 的 state_detail_all。"""
    with lock:
        out = []
        for name, on in state["switches"].items():
            out.append(state_event("switch", name, on))
        for name, on in state["mppt"].items():
            out.append(state_event("switch", name, on))
        for name, v in state["sensors"].items():
            out.append(state_event("sensor", name, v))
        for name, v in state["texts"].items():
            out.append(state_event("text_sensor", name, v, is_text=True))
        for name, v in state["numbers"].items():
            out.append(state_event("number", name, v))
        return b"".join(out)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass  # 静音，避免刷屏

    def _send(self, code, body, ctype="text/html; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/dashboard"):
            self._send(200, INDEX.read_bytes())
        elif path == "/events":
            self.stream_events()
        else:
            self._send(404, b"not found", "text/plain")

    def stream_events(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        try:
            self.wfile.write(full_snapshot())
            self.wfile.flush()
            last_ping = time.time()
            while True:
                # 模拟实时漂移：光伏功率波动 + 库仑计电流变化
                with lock:
                    if "SolarPower 发电功率" in state["sensors"]:
                        st = state["sensors"]
                        st["SolarPower 发电功率"] = max(
                            0.0, min(900.0, st["SolarPower 发电功率"] + random.uniform(-18, 18)))
                        st["SolarChg 充电电流"] = st["SolarPower 发电功率"] / 52.6
                        if st.get("CoulombSOC 电量百分比") is not None:
                            st["CoulombSOC 电量百分比"] = min(
                                100.0, st["CoulombSOC 电量百分比"] + random.uniform(0, 0.01))
                for name in ("SolarPower 发电功率", "SolarChg 充电电流", "CoulombSOC 电量百分比"):
                    with lock:
                        v = state["sensors"].get(name)
                    if v is not None:
                        self.wfile.write(state_event("sensor", name, round(v, 2)))

                now = time.time()
                if now - last_ping >= 5:
                    last_ping = now
                    self.wfile.write(ev("ping", {
                        "title": "485网关", "comment": "", "ota": True,
                        "log": True, "lang": "zh", "uptime": int(now - boot_time),
                    }))
                    # 只推未发过的日志（真实 ESPHome 是逐条推，不是重复最后一条）
                    with lock:
                        pending = LOG_LINES[log_sent[0]:]
                        log_sent[0] = len(LOG_LINES)
                    for line in pending:
                        self.wfile.write(ev("log", line))
                self.wfile.flush()
                time.sleep(1.0)
        except (BrokenPipeError, ConnectionResetError):
            pass  # 浏览器关闭页面

    def do_POST(self):
        path = unquote(urlparse(self.path).path)
        parts = [p for p in path.split("/") if p]
        # /<domain>/<name>/<action>[?value=x]
        if len(parts) < 3:
            self._send(400, b"bad request", "text/plain")
            return
        domain, name, action = parts[0], "/".join(parts[1:-1]), parts[-1]
        msg = f"POST {domain}/{name}/{action}"

        with lock:
            if domain == "switch" and name in state["switches"]:
                if action == "toggle":
                    state["switches"][name] = not state["switches"][name]
                elif action == "turn_on":
                    state["switches"][name] = True
                elif action == "turn_off":
                    state["switches"][name] = False
                val = state["switches"][name]
                log(f"{msg} → {'ON' if val else 'OFF'}")
                self._send(200, f"{'ON' if val else 'OFF'}".encode(), "text/plain")
                return
            if domain == "switch" and name in state["mppt"]:
                state["mppt"][name] = (not state["mppt"][name]) if action == "toggle" \
                    else action == "turn_on"
                log(msg)
                self._send(200, b"OK", "text/plain")
                return
            if domain == "number" and name in state["numbers"] and action == "set":
                q = urlparse(self.path).query
                for kv in q.split("&"):
                    if kv.startswith("value="):
                        state["numbers"][name] = float(kv[6:])
                        log(f"{msg} value={state['numbers'][name]}")
                self._send(200, b"OK", "text/plain")
                return
            if domain == "button" and action == "press":
                log(msg)
                self._send(200, b"OK", "text/plain")
                return
        log(f"{msg} (未知实体)")
        self._send(404, b"unknown entity", "text/plain")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8321)
    ap.add_argument("--no-coulomb", action="store_true", help="模拟库仑计未上线")
    ap.add_argument("--no-trend", action="store_true", help="不注入充电趋势，验证空态")
    ap.add_argument("--scene", type=int, default=0, help="场景页初始档位 0/1/2")
    args = ap.parse_args()

    if args.no_coulomb:
        for k in [k for k in state["sensors"] if k.startswith("Coulomb")]:
            del state["sensors"][k]
    if args.scene:
        state["sensors"]["SceneLight 灯光模式"] = float(args.scene)

    # 充电趋势：生成"白天发电"钟形曲线（24h / 每 5 分钟 = 288 点）。
    # 编码与固件完全一致："v1:<count>:<idx>:<base64>"，uint16 小端，时间正序（最旧→最新）
    if not args.no_trend:
        import base64
        import struct
        CAP = 288
        vals = []
        now_ts = time.time()
        for k in range(CAP):
            sec_ago = (CAP - 1 - k) * 300          # 第 k 点 = (CAP-1-k)×5 分钟前
            lt = time.localtime(now_ts - sec_ago)
            h = lt.tm_hour + lt.tm_min / 60.0
            if 6.0 <= h <= 18.5:                   # 太阳 6:00~18:30，正午最强
                w = math.sin((h - 6.0) / 12.5 * math.pi) * 760 + random.uniform(-40, 40)
            else:
                w = 0.0
            vals.append(max(0, min(65535, int(w))))
        raw = b"".join(struct.pack("<H", v) for v in vals)
        b64 = base64.b64encode(raw).decode()
        state["texts"]["SolarTrend 充电趋势"] = f"v1:{CAP}:0:{b64}"
        log(f"[preview] trend injected: {CAP} pts, {len(b64)} chars")

    log("preview server started")
    log("[di] addr=0x02 key=X4")
    log("[stat] poll=off upload-only")

    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"面板预览: http://127.0.0.1:{args.port}/dashboard")
    if args.no_coulomb:
        print("  (库仑计未上线模式)")
    print("Ctrl-C 停止")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
