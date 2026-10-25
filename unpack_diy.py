#!/usr/bin/env python3
"""还原 .diy 容器（干净室复刻）。

步骤:
  1. 剥离尾部诱饵(连续 TXT<n>\\n 行 + 可解析的 zip);
  2. 头部 min(1024, len) 字节再 XOR 1 -> 原始文件。

用法:

    python unpack_diy.py <输入.diy> <输出文件>
"""

from __future__ import annotations

import argparse
import io
import struct
import sys
import zipfile
from pathlib import Path

XOR_LEN = 1024


def xor_prefix(buf: bytearray) -> None:
    for i in range(min(XOR_LEN, len(buf))):
        buf[i] ^= 1


def valid_zip_at(data: bytes, off: int) -> bool:
    if data[off:off + 4] != b"PK\x03\x04":
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(data[off:])) as zf:
            return zf.testzip() is None
    except zipfile.BadZipFile:
        return False


def find_junk_offset(data: bytes) -> int:
    """返回诱饵起始偏移; 未发现返回 -1.

    从 zip 起点向后按 ``TXT<digits>\\n`` 自定界格式回扫,
    不依赖 payload 尾部是否有换行.
    """
    idx = data.rfind(b"PK\x03\x04")
    if idx <= 0 or not valid_zip_at(data, idx):
        return -1
    cur = idx
    while cur > 0 and data[cur - 1] == 0x0A:
        j = cur - 1  # 指向行尾 '\n'
        k = j
        while k > 0 and 0x30 <= data[k - 1] <= 0x39:  # 回扫数字
            k -= 1
        if k == j or k < 3 or data[k - 3:k] != b"TXT":
            break
        cur = k - 3
    return cur if cur < idx else -1


def describe_pe(data: bytes) -> str:
    """若还是 PE, 附带一句头校验(仅信息输出)."""
    if len(data) < 0x40 or data[:2] != b"MZ":
        return "not MZ"
    (e_lfanew,) = struct.unpack_from("<I", data, 0x3C)
    if e_lfanew + 4 > len(data) or data[e_lfanew:e_lfanew + 4] != b"PE\0\0":
        return f"MZ but bad PE at 0x{e_lfanew:x}"
    machine, nsec = struct.unpack_from("<HH", data, e_lfanew + 4)
    return f"PE ok (machine=0x{machine:04x}, sections={nsec})"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="还原 .diy 容器")
    ap.add_argument("input", type=Path, help="输入 .diy")
    ap.add_argument("output", type=Path, help="输出原始文件")
    args = ap.parse_args(argv[1:])

    data = bytearray(args.input.read_bytes())
    junk = find_junk_offset(bytes(data))
    if junk > 0:
        print(f"[*] tail junk at {junk}, stripping")
        del data[junk:]
    else:
        print("[*] no tail junk")
    print(f"[*] before xor: {describe_pe(bytes(data))}")
    xor_prefix(data)
    print(f"[*] after  xor: {describe_pe(bytes(data))}")
    args.output.write_bytes(bytes(data))
    print(f"[+] written {args.output} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
