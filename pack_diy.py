#!/usr/bin/env python3
"""生产 .diy 容器文件（干净室复刻）。

容器布局:

    [XOR'd payload][TXT 诱饵行 ...][zip(data.txt)]

- XOR 仅作用于 payload 头部 min(1024, len) 字节;
- 诱饵追加在镜像末尾(节表之外), 不参与 PE 映射。

用法:

    python pack_diy.py <输入文件> <输出.diy> [--no-junk] [--seed N]
"""

from __future__ import annotations

import argparse
import io
import random
import sys
import zipfile
from pathlib import Path

XOR_LEN = 1024
TXT_LINES = 100
ZIP_LINES = 100


def xor_prefix(buf: bytearray) -> None:
    """把前 XOR_LEN 字节逐字节 XOR 1 (就地)."""
    for i in range(min(XOR_LEN, len(buf))):
        buf[i] ^= 1


def build_tail(rng: random.Random) -> bytes:
    """构造诱饵: TXT 行 + 含 data.txt 的 zip."""
    txt = b"".join(
        f"TXT{rng.randint(0, 99)}\n".encode() for _ in range(TXT_LINES)
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "data.txt",
            "".join(f"DIY{rng.randint(0, 99)}\n" for _ in range(ZIP_LINES)),
        )
    return txt + buf.getvalue()


def pack(payload: bytes, *, junk: bool = True, seed: int | None = None) -> bytes:
    data = bytearray(payload)
    xor_prefix(data)
    if not junk:
        return bytes(data)
    return bytes(data) + build_tail(random.Random(seed))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="生产 .diy 容器")
    ap.add_argument("input", type=Path, help="输入文件(任意二进制)")
    ap.add_argument("output", type=Path, help="输出 .diy 路径")
    ap.add_argument("--no-junk", action="store_true",
                    help="只输出 XOR 部分, 不追加诱饵")
    ap.add_argument("--seed", type=int, default=None,
                    help="固定诱饵随机数种子(便于复现)")
    args = ap.parse_args(argv[1:])

    payload = args.input.read_bytes()
    out = pack(payload, junk=not args.no_junk, seed=args.seed)
    args.output.write_bytes(out)
    print(f"[*] payload={len(payload)} -> {args.output} ({len(out)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
