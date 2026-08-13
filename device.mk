#
# Copyright (C) 2026 The Android Open Source Project
# Copyright (C) 2026 SebaUbuntu's TWRP device tree generator
#
# SPDX-License-Identifier: Apache-2.0
#

LOCAL_PATH := device/zte/P720S20

# The device uses dynamic logical partitions, but this recovery build must not
# try to assemble a replacement super image.
PRODUCT_USE_DYNAMIC_PARTITIONS := true
PRODUCT_BUILD_SUPER_PARTITION := false

# Build the BootControl implementation against the same Android 12.1
# userspace as fastbootd. It overlays the incompatible stock Android 13
# implementation from the seeded vendor ramdisk.
PRODUCT_PACKAGES += android.hardware.boot@1.2-impl

# Keep the product lean: the stock first-stage fstab and vendor kernel modules
# are injected into the recovery root by BOARD_RECOVERY_IMAGE_PREPARE.
PRODUCT_SOONG_NAMESPACES += \
    $(LOCAL_PATH)
