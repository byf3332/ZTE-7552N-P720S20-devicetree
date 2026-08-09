#!/usr/bin/env python3

import sys
from pathlib import Path

# These stock Android 13 service-context files name types that do not exist in
# the TWRP 12.1 recovery policy. They are outside first_stage_ramdisk and are
# not needed after force_normal_boot switches to the first-stage root.
STOCK_SERVICE_CONTEXTS = (
    "plat_service_contexts",
    "product_service_contexts",
    "system_ext_service_contexts",
    "vendor_service_contexts",
)

# Keep stock directories as mount points instead of replacing them with the
# generated recovery-root symlinks.
TWRP_MOUNT_POINT_LINKS = (
    "product",
    "system_ext",
)

REQUIRED_TWRP_FILES = (
    "sepolicy",
    "prop.default",
    "plat_file_contexts",
    "vendor_file_contexts",
    "system/bin/init",
    "system/bin/recovery",
    "system/etc/recovery.fstab",
    "init.recovery.common.rc",
    "init.recovery.ums9620.rc",
    "init.recovery.ums9620_2h10.rc",
    "vendor/etc/vintf/manifest.xml",
    "system/bin/hw/android.hardware.gatekeeper@1.0-service.trusty",
    "system/bin/hw/android.hardware.security.keymint@2.0-unisoc.service.trusty",
    "system/lib64/p720s20-keymint/android.hardware.gatekeeper@1.0.so",
    "system/lib64/p720s20-keymint/android.hardware.security.keymint-V1-ndk.so",
    "system/lib64/p720s20-keymint/android.hardware.security.keymint-V2-ndk.so",
    "system/lib64/p720s20-keymint/android.hardware.security.secureclock-V1-ndk.so",
    "system/lib64/p720s20-keymint/android.hardware.security.sharedsecret-V1-ndk.so",
    "system/lib64/p720s20-keymint/lib_android_keymaster_keymint_utils.so",
    "system/lib64/p720s20-keymint/libkeymaster_messages.so",
    "system/lib64/p720s20-keymint/libkeymaster_portable.so",
    "system/lib64/p720s20-keymint/libkeymint.so",
    "system/lib64/p720s20-keymint/libpuresoftkeymasterdevice.so",
    "system/lib64/p720s20-keymint/libtrusty.so",
    "system/lib64/p720s20-keymint/libtrustyHalHelper.so",
)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            f"usage: {sys.argv[0]} "
            "TARGET_VENDOR_RAMDISK_OUT TARGET_RECOVERY_ROOT_OUT"
        )

    vendor_root = Path(sys.argv[1])
    recovery_root = Path(sys.argv[2])

    if not vendor_root.is_dir():
        raise SystemExit(f"vendor ramdisk root does not exist: {vendor_root}")

    if not recovery_root.is_dir():
        raise SystemExit(f"recovery root does not exist: {recovery_root}")

    for relative in REQUIRED_TWRP_FILES:
        path = recovery_root / relative
        if not path.is_file():
            raise SystemExit(
                f"required TWRP recovery file is missing: {path}"
            )

    for relative in STOCK_SERVICE_CONTEXTS:
        path = vendor_root / relative
        if not path.is_file():
            raise SystemExit(f"stock service-context file is missing: {path}")
        path.unlink()

    for relative in TWRP_MOUNT_POINT_LINKS:
        stock_path = vendor_root / relative
        twrp_path = recovery_root / relative
        if not stock_path.is_dir() or stock_path.is_symlink():
            raise SystemExit(
                f"stock mount-point directory is missing: {stock_path}"
            )
        if not twrp_path.is_symlink():
            raise SystemExit(
                f"expected TWRP mount-point symlink is missing: {twrp_path}"
            )
        twrp_path.unlink()

    print(
        "Prepared stock/TWRP ramdisk boundary: removed stock service "
        "contexts and preserved stock product/system_ext mount points"
    )


if __name__ == "__main__":
    main()
