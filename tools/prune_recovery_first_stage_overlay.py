#!/usr/bin/env python3

import shutil
import sys
from pathlib import Path

STOCK_EARLY_INIT_PATHS = (
    "sepolicy",
    "prop.default",
    "file_contexts",
    "file_contexts.bin",
    "odm_file_contexts",
    "odm_property_contexts",
    "plat_file_contexts",
    "plat_property_contexts",
    "product_file_contexts",
    "product_property_contexts",
    "system_ext_file_contexts",
    "system_ext_property_contexts",
    "vendor_file_contexts",
    "vendor_property_contexts",
    "product",
    "system_ext",
)

REQUIRED_TWRP_PATHS = (
    "system/bin/init",
    "system/bin/recovery",
    "system/etc/recovery.fstab",
    "init.recovery.common.rc",
    "init.recovery.ums9620.rc",
    "init.recovery.ums9620_2h10.rc",
)


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    else:
        raise SystemExit(f"expected TWRP overlay path is missing: {path}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            f"usage: {sys.argv[0]} TARGET_RECOVERY_ROOT_OUT"
        )

    root = Path(sys.argv[1])

    if not root.is_dir():
        raise SystemExit(f"recovery root does not exist: {root}")

    for relative in REQUIRED_TWRP_PATHS:
        path = root / relative
        if not (path.is_file() or path.is_symlink()):
            raise SystemExit(
                f"required TWRP recovery path is missing: {path}"
            )

    removed = []

    for relative in STOCK_EARLY_INIT_PATHS:
        path = root / relative
        remove_path(path)
        removed.append(relative)

    for relative in STOCK_EARLY_INIT_PATHS:
        path = root / relative
        if path.exists() or path.is_symlink():
            raise SystemExit(
                f"failed to prune TWRP early-init path: {path}"
            )

    print(
        "Pruned TWRP early-init overlay; "
        "stock PLATFORM copies remain effective: "
        + ", ".join(removed)
    )


if __name__ == "__main__":
    main()
