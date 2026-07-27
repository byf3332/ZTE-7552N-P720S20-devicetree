#!/usr/bin/env python3
"""Inspect a P720S20 vendor_boot v4 image before device-side testing."""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

MAGIC = b"VNDRBOOT"
V4_HEADER_SIZE = 2128
ENTRY_SIZE = 108
TYPE_NAMES = {0: "NONE", 1: "PLATFORM", 2: "RECOVERY", 3: "DLKM"}

EXPECTED = {
    "header_version": 4,
    "page_size": 4096,
    "kernel_addr": 0x00008000,
    "ramdisk_addr": 0x05400000,
    "tags_addr": 0x00000100,
    "header_size": 2128,
    "dtb_size": 170052,
    "dtb_addr": 0x01F00000,
    "table_entry_num": 1,
    "table_entry_size": 108,
    "bootconfig_size": 0,
    "cmdline": "console=ttyS1,115200n8 buildvariant=user",
}


def align(value: int, size: int) -> int:
    return (value + size - 1) // size * size


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")


def ok(msg: str) -> None:
    print(f"[ OK ] {msg}")


def check(name: str, value, expected) -> bool:
    if value == expected:
        ok(f"{name}: {value!r}")
        return True
    fail(f"{name}: got {value!r}, expected {expected!r}")
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    args = ap.parse_args()

    blob = args.image.read_bytes()
    if len(blob) < V4_HEADER_SIZE:
        fail("image is too small to contain a vendor_boot v4 header")
        return 2
    if blob[:8] != MAGIC:
        fail(f"bad magic: {blob[:8]!r}")
        return 2

    header_version, page_size, kernel_addr, ramdisk_addr, ramdisk_size = struct.unpack_from(
        "<IIIII", blob, 8
    )
    cmdline = blob[28:2076].split(b"\0", 1)[0].decode("ascii", errors="replace")
    tags_addr = struct.unpack_from("<I", blob, 2076)[0]
    name = blob[2080:2096].split(b"\0", 1)[0].decode("ascii", errors="replace")
    header_size = struct.unpack_from("<I", blob, 2096)[0]
    dtb_size = struct.unpack_from("<I", blob, 2100)[0]
    dtb_addr = struct.unpack_from("<Q", blob, 2104)[0]
    table_size, entry_num, entry_size, bootconfig_size = struct.unpack_from("<IIII", blob, 2112)

    checks = [
        check("header_version", header_version, EXPECTED["header_version"]),
        check("page_size", page_size, EXPECTED["page_size"]),
        check("kernel_addr", kernel_addr, EXPECTED["kernel_addr"]),
        check("ramdisk_addr", ramdisk_addr, EXPECTED["ramdisk_addr"]),
        check("tags_addr", tags_addr, EXPECTED["tags_addr"]),
        check("header_size", header_size, EXPECTED["header_size"]),
        check("dtb_size", dtb_size, EXPECTED["dtb_size"]),
        check("dtb_addr", dtb_addr, EXPECTED["dtb_addr"]),
        check("table_entry_num", entry_num, EXPECTED["table_entry_num"]),
        check("table_entry_size", entry_size, EXPECTED["table_entry_size"]),
        check("bootconfig_size", bootconfig_size, EXPECTED["bootconfig_size"]),
        check("cmdline", cmdline, EXPECTED["cmdline"]),
    ]

    print(f"[INFO] image_size: {len(blob)}")
    print(f"[INFO] vendor_ramdisk_size: {ramdisk_size}")
    print(f"[INFO] board name: {name!r}")
    print(f"[INFO] vendor_ramdisk_table_size: {table_size}")

    ramdisk_off = page_size
    if blob[ramdisk_off:ramdisk_off + 4] == b"\x02\x21\x4c\x18":
        ok("vendor ramdisk compression: legacy LZ4")
    else:
        fail(
            "vendor ramdisk does not start with legacy LZ4 magic "
            f"(got {blob[ramdisk_off:ramdisk_off + 4].hex()})"
        )
        checks.append(False)

    dtb_off = ramdisk_off + align(ramdisk_size, page_size)
    table_off = dtb_off + align(dtb_size, page_size)
    if table_off + table_size > len(blob):
        fail("vendor ramdisk table lies outside the image")
        return 2

    if entry_num:
        entry = blob[table_off:table_off + entry_size]
        entry_ramdisk_size, entry_ramdisk_offset, entry_type = struct.unpack_from("<III", entry, 0)
        entry_name = entry[12:44].split(b"\0", 1)[0].decode("ascii", errors="replace")
        board_id = struct.unpack_from("<16I", entry, 44)

        print(f"[INFO] entry[0].size: {entry_ramdisk_size}")
        print(f"[INFO] entry[0].offset: {entry_ramdisk_offset}")
        print(f"[INFO] entry[0].type: {entry_type} ({TYPE_NAMES.get(entry_type, 'UNKNOWN')})")
        print(f"[INFO] entry[0].name: {entry_name!r}")
        print(f"[INFO] entry[0].board_id: {board_id}")

        checks.append(check("entry[0].type", entry_type, 1))
        checks.append(check("entry[0].name", entry_name, ""))
        checks.append(check("entry[0].offset", entry_ramdisk_offset, 0))
        checks.append(check("entry[0].size", entry_ramdisk_size, ramdisk_size))
        checks.append(check("entry[0].board_id", board_id, (0,) * 16))

    if all(checks):
        print("\nPASS: vendor_boot structure matches the stock P720S20 v4 layout.")
        return 0

    print("\nFAIL: one or more structural fields differ from stock.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
