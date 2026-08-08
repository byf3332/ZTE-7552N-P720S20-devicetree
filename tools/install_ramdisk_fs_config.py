#!/usr/bin/env python3

import struct
import sys
from pathlib import Path

PATH = "first_stage_ramdisk/system/bin/fsck.f2fs"


def align8(value):
    return (value + 7) & ~7


def make_record():
    raw_path = PATH.encode("utf-8") + b"\0"
    raw_path += b"\0" * (align8(len(raw_path)) - len(raw_path))

    length = 16 + len(raw_path)

    return (
        struct.pack(
            "<HHHHQ",
            length,
            0o755,
            0,
            0,
            0,
        )
        + raw_path
    )


def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            f"usage: {sys.argv[0]} TARGET_OUT"
        )

    target_out = Path(sys.argv[1])
    config = target_out / "etc" / "fs_config_files"
    config.parent.mkdir(parents=True, exist_ok=True)

    record = make_record()
    existing = config.read_bytes() if config.exists() else b""

    if not existing.startswith(record):
        config.write_bytes(record + existing)

    print(
        "Installed ramdisk fs_config override: "
        f"{PATH} -> 0755"
    )


if __name__ == "__main__":
    main()
