#!/usr/bin/env python3
"""
485 总线抓包脚本 —— 监听 S3 是否真的把帧发到了总线上

用法：
    python3 tools/rs485_listen.py /dev/cu.usbserial-XXXX

接线：
    USB-485 转换器 A/B 并联到总线（与 S3、485模块 共地）
    转换器插到 Mac

注意：
    1. 必须关掉厂家 PC 软件（它占用转换器串口）
    2. 必须停止 PC 软件轮询，否则两个主站抢总线
    3. 运行后按 S3 web 页面的 probe 按钮

判读：
    收到 03 05 00 00 FF 00 8D D8  → S3 发送正常，问题在模块侧
    收到碎片/乱码                 → 发送被破坏（总线质量）
    完全没收到                    → 帧没上总线（DE/DI 问题）
"""

import sys
import time

try:
    import serial
except ImportError:
    print("缺少 pyserial，请先安装：")
    print("    python3 -m pip install pyserial")
    sys.exit(1)


def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def looks_like_modbus(buf: bytes) -> bool:
    """粗判缓冲里是否有合法 Modbus 帧"""
    for i in range(len(buf) - 4):
        addr = buf[i]
        fc = buf[i + 1]
        if addr not in (1, 2, 3, 5, 0x10):
            continue
        if fc not in (1, 2, 3, 4, 5, 6, 0x0F, 0x10):
            continue
        # 尝试按常见长度校验
        for length in (6, 7, 8, 9, 19):
            if i + length > len(buf):
                continue
            frame = buf[i:i + length]
            body, got = frame[:-2], frame[-1] << 8 | frame[-2]
            if crc16(body) == got:
                return True
    return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("可用的串口：")
        import glob
        for p in sorted(glob.glob('/dev/cu.*')):
            print("   ", p)
        sys.exit(1)

    port = sys.argv[1]
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 38400
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 30

    print(f"打开 {port} @ {baud} 8N1 ...")
    try:
        ser = serial.Serial(port, baud, bytesize=8, parity='N',
                            stopbits=1, timeout=0.1)
    except Exception as e:
        print(f"打开失败：{e}")
        print("  - 串口被占用？关掉厂家 PC 软件")
        print("  - 口名对不对？ls /dev/cu.*")
        sys.exit(1)

    print(f"监听 {duration} 秒 —— 现在去按 S3 的 probe 按钮 / 点开关")
    print("=" * 60)

    t0 = time.time()
    total = b''
    last = 0.0
    try:
        while time.time() - t0 < duration:
            chunk = ser.read(512)
            if chunk:
                total += chunk
                now = time.time() - t0
                # 每收到一批就打印十六进制
                print(f"[{now:6.2f}s] {chunk.hex(' ')}")
                last = now
    except KeyboardInterrupt:
        print("\n[中断]")
    finally:
        ser.close()

    print("=" * 60)
    print(f"共收到 {len(total)} 字节")
    if total:
        print("完整十六进制：")
        print("   ", total.hex(' '))
        if looks_like_modbus(total):
            print("\n✅ 检测到合法 Modbus 帧 —— S3 确实发出去了")
        else:
            print("\n⚠️ 有数据但没有合法 Modbus 帧（可能被干扰/截断）")
    else:
        print("\n❌ 一个字节都没收到 —— S3 的帧没有上总线")
        print("   检查：DE 是否切换 / DI 是否接到 GPIO15 / 转换器 A-B 是否接对")


if __name__ == '__main__':
    main()
