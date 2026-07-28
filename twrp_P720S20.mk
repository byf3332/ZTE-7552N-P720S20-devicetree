#
# Copyright (C) 2026 The Android Open Source Project
# Copyright (C) 2026 SebaUbuntu's TWRP device tree generator
#
# SPDX-License-Identifier: Apache-2.0
#

# This branch builds a temporary recovery-as-boot image only.
PRODUCT_BUILD_VENDOR_BOOT_IMAGE := false

# 64-bit recovery userspace.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)

# Base AOSP product. Required to populate TARGET_ROOT_OUT used by recovery packaging.
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Android devices without a dedicated recovery partition use the generic
# ramdisk model and place recovery resources in vendor_boot.
$(call inherit-product, $(SRC_TARGET_DIR)/product/generic_ramdisk.mk)

# TWRP common configuration.
$(call inherit-product, vendor/twrp/config/common.mk)

# Device-specific configuration.
$(call inherit-product, device/zte/P720S20/device.mk)

PRODUCT_DEVICE := P720S20
PRODUCT_NAME := twrp_P720S20
PRODUCT_BRAND := ZTE
PRODUCT_MODEL := ZTE 7552N
PRODUCT_MANUFACTURER := zte

PRODUCT_GMS_CLIENTID_BASE := android-zte

PRODUCT_BUILD_PROP_OVERRIDES += \
    PRIVATE_BUILD_DESC="ums9620_2h10_native-user 13 TP1A.220624.014 20240920.145249 release-keys"

BUILD_FINGERPRINT := ZTE/CN_P720S20/P720S20:13/TP1A.220624.014/20240920.145249:user/release-keys
