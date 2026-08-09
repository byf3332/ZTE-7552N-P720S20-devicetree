#!/usr/bin/env python3

import sys
from pathlib import Path

FIRST_STAGE_FSTABS = (
    "first_stage_ramdisk/fstab.ums9620_1h10",
    "first_stage_ramdisk/fstab.ums9620_2h10",
    "first_stage_ramdisk/fstab.ums9620_2h10_uob",
    "first_stage_ramdisk/fstab.ums9620_2h10_uob_marlin3",
)

EXPECTED_AVB_FLAGS = 7
EXPECTED_AVB_KEY_FLAGS = 2


def rewrite_fstab(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"first-stage fstab is missing: {path}")

    original = path.read_text(encoding="utf-8")
    output = []
    avb_flags = 0
    avb_key_flags = 0

    for source_line in original.splitlines(keepends=True):
        newline = "\n" if source_line.endswith("\n") else ""
        line = source_line.rstrip("\r\n")

        if not line.strip() or line.lstrip().startswith("#"):
            output.append(line + newline)
            continue

        fields = line.split()
        if len(fields) != 5:
            raise SystemExit(f"unexpected fstab line in {path}: {line}")

        kept_flags = []
        for flag in fields[4].split(","):
            if flag == "avb" or flag.startswith("avb="):
                avb_flags += 1
            elif flag == "avb_keys" or flag.startswith("avb_keys="):
                avb_key_flags += 1
            else:
                kept_flags.append(flag)

        if not kept_flags:
            raise SystemExit(f"empty fs_mgr flags after AVB removal: {line}")

        fields[4] = ",".join(kept_flags)
        output.append(" ".join(fields) + newline)

    if avb_flags != EXPECTED_AVB_FLAGS:
        raise SystemExit(
            f"unexpected AVB flag count in {path}: "
            f"{avb_flags}, expected {EXPECTED_AVB_FLAGS}"
        )

    if avb_key_flags != EXPECTED_AVB_KEY_FLAGS:
        raise SystemExit(
            f"unexpected AVB key flag count in {path}: "
            f"{avb_key_flags}, expected {EXPECTED_AVB_KEY_FLAGS}"
        )

    rewritten = "".join(output)
    if "avb=" in rewritten or "avb_keys" in rewritten:
        raise SystemExit(f"AVB flags remain in first-stage fstab: {path}")

    path.write_text(rewritten, encoding="utf-8")
    print(
        f"Disabled Android first-stage AVB in {path}: "
        f"removed {avb_flags} avb flags and "
        f"{avb_key_flags} avb_keys flags"
    )


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            f"usage: {sys.argv[0]} RAMDISK_ROOT [RAMDISK_ROOT ...]"
        )

    for argument in sys.argv[1:]:
        root = Path(argument)
        if not root.is_dir():
            raise SystemExit(f"ramdisk root does not exist: {root}")

        for relative in FIRST_STAGE_FSTABS:
            rewrite_fstab(root / relative)


if __name__ == "__main__":
    main()
