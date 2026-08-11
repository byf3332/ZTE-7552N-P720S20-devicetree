#
# Copyright (C) 2026 The Android Open Source Project
# Copyright (C) 2026 SebaUbuntu's TWRP device tree generator
#
# SPDX-License-Identifier: Apache-2.0
#

DEVICE_PATH := device/zte/P720S20

# Minimal TWRP manifest
ALLOW_MISSING_DEPENDENCIES := true

# A/B
AB_OTA_UPDATER := true
AB_OTA_PARTITIONS += \
    boot \
    vendor_boot \
    dtbo \
    vbmeta \
    vbmeta_system \
    vbmeta_vendor \
    odm \
    product \
    system \
    system_ext \
    vendor \
    vendor_dlkm

# Architecture
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_ABI2 :=
TARGET_CPU_VARIANT := generic
TARGET_CPU_VARIANT_RUNTIME := cortex-a76

TARGET_2ND_ARCH := arm
TARGET_2ND_ARCH_VARIANT := armv7-a-neon
TARGET_2ND_CPU_ABI := armeabi-v7a
TARGET_2ND_CPU_ABI2 := armeabi
TARGET_2ND_CPU_VARIANT := generic
TARGET_2ND_CPU_VARIANT_RUNTIME := cortex-a55

# Bootloader / platform
TARGET_BOARD_PLATFORM := ums9620
TARGET_BOOTLOADER_BOARD_NAME := ums9620_2h10
TARGET_NO_BOOTLOADER := true

# Display
TARGET_SCREEN_DENSITY := 213
TARGET_RECOVERY_PIXEL_FORMAT := RGBX_8888

# Stock vendor_boot v4 geometry
TARGET_NO_KERNEL := true
BOARD_BOOT_HEADER_VERSION := 4
BOARD_PAGE_SIZE := 4096
BOARD_KERNEL_PAGESIZE := 4096
BOARD_KERNEL_BASE := 0x00000000
BOARD_KERNEL_OFFSET := 0x00008000
BOARD_RAMDISK_OFFSET := 0x05400000
BOARD_TAGS_OFFSET := 0x00000100
BOARD_DTB_OFFSET := 0x01f00000
BOARD_HEADER_SIZE := 2128
BOARD_VENDOR_CMDLINE := console=ttyS1,115200n8 buildvariant=user

# Stock vendor ramdisk uses legacy LZ4.
BOARD_RAMDISK_USE_LZ4 := true

# Stock DTB extracted from vendor_boot.
TARGET_PREBUILT_DTB := $(DEVICE_PATH)/prebuilt/dtb.img

BOARD_MKBOOTIMG_ARGS += --header_version $(BOARD_BOOT_HEADER_VERSION)
BOARD_MKBOOTIMG_ARGS += --pagesize $(BOARD_PAGE_SIZE)
BOARD_MKBOOTIMG_ARGS += --base $(BOARD_KERNEL_BASE)
BOARD_MKBOOTIMG_ARGS += --kernel_offset $(BOARD_KERNEL_OFFSET)
BOARD_MKBOOTIMG_ARGS += --ramdisk_offset $(BOARD_RAMDISK_OFFSET)
BOARD_MKBOOTIMG_ARGS += --tags_offset $(BOARD_TAGS_OFFSET)
BOARD_MKBOOTIMG_ARGS += --dtb_offset $(BOARD_DTB_OFFSET)
BOARD_MKBOOTIMG_ARGS += --vendor_cmdline "$(BOARD_VENDOR_CMDLINE)"
BOARD_MKBOOTIMG_ARGS += --dtb $(TARGET_PREBUILT_DTB)

# Partitions
BOARD_FLASH_BLOCK_SIZE := 262144
BOARD_BOOTIMAGE_PARTITION_SIZE := 67108864
BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE := 104857600
BOARD_HAS_LARGE_FILESYSTEM := true
BOARD_USES_METADATA_PARTITION := true
BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE := f2fs

TARGET_COPY_OUT_VENDOR := vendor
TARGET_USERIMAGES_USE_EXT4 := true
TARGET_USERIMAGES_USE_F2FS := true
TARGET_USERIMAGES_USE_EROFS := true
TARGET_USES_MKE2FS := true

# No standalone recovery partition.
# Stock vendor_boot has one PLATFORM vendor-ramdisk entry and no RECOVERY fragment.
BOARD_USES_RECOVERY_AS_BOOT :=
BOARD_USES_GENERIC_KERNEL_IMAGE := true
BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true
BOARD_EXCLUDE_KERNEL_FROM_RECOVERY_IMAGE :=
BOARD_MOVE_GSI_AVB_KEYS_TO_VENDOR_BOOT := true
TARGET_NO_RECOVERY := true

# Deliberately NOT set:
# BOARD_INCLUDE_RECOVERY_RAMDISK_IN_VENDOR_BOOT
# Setting it would create a separate VENDOR_RAMDISK_TYPE_RECOVERY fragment,
# which does not match the stock P720S20 vendor_boot layout.

TARGET_RECOVERY_FSTAB := $(DEVICE_PATH)/recovery.fstab

# Seed the PLATFORM ramdisk with the complete stock vendor ramdisk.
# Disable Android first-stage AVB because this device's TrustOS bypass does not
# affect libfs_avb after Linux starts. Keep TWRP's recovery policy and contexts.
BOARD_RECOVERY_IMAGE_PREPARE = python3 $(DEVICE_PATH)/tools/extract_stock_vendor_ramdisk.py $(DEVICE_PATH)/prebuilt/vendor_ramdisk_stock.lz4 $(TARGET_VENDOR_RAMDISK_OUT) $(LZ4) && python3 $(DEVICE_PATH)/tools/install_ramdisk_fs_config.py $(TARGET_OUT) && cp -a $(DEVICE_PATH)/recovery/root/. $(TARGET_RECOVERY_ROOT_OUT)/ && python3 $(DEVICE_PATH)/tools/disable_first_stage_avb.py $(TARGET_VENDOR_RAMDISK_OUT) $(TARGET_RECOVERY_ROOT_OUT) && python3 $(DEVICE_PATH)/tools/prepare_recovery_ramdisks.py $(TARGET_VENDOR_RAMDISK_OUT) $(TARGET_RECOVERY_ROOT_OUT)

# Recovery SELinux: first bring-up uses a permissive recovery policy while
# retaining the stock Unisoc init fragment.
TARGET_RECOVERY_SELINUX := permissive
TW_HAS_SELINUX := true

# Filesystems / dynamic partitions
TW_INCLUDE_EXT4 := true
TW_INCLUDE_F2FS := true
TW_INCLUDE_EROFS := true
TW_INCLUDE_VFAT := true
TW_INCLUDE_LPDUMP := true

# Android 13 FBE metadata encryption. The recovery root supplies the Unisoc
# Trusty KeyMint 2.0/Gatekeeper services and their compatible VINTF manifest.
TW_INCLUDE_CRYPTO := true
TW_RECOVERY_ADDITIONAL_RELINK_LIBRARY_FILES += $(TARGET_OUT_SHARED_LIBRARIES)/libresetprop.so
TW_INCLUDE_CRYPTO_FBE := true
TW_INCLUDE_FBE_METADATA_DECRYPT := true
TW_HAS_DATA_MEDIA := true
TW_USE_FSCRYPT_POLICY := 2
TW_FORCE_KEYMASTER_VER := true

# TWRP
TW_THEME := portrait_hdpi
TW_EXTRA_LANGUAGES := true
TW_DEFAULT_LANGUAGE := zh_CN
TW_INPUT_BLACKLIST := "hbtp_vm"
TW_USE_LEGACY_BATTERY_SERVICES := true
TW_CUSTOM_CPU_TEMP_PATH := "/sys/class/thermal/thermal_zone4/temp"
TW_EXCLUDE_TWRPAPP := true
TW_NO_FLASH_CURRENT_TWRP := true
# Stock init.recovery.common.rc owns the Unisoc configfs USB gadget setup.
TW_EXCLUDE_DEFAULT_USB_INIT := true
TW_USE_TOOLBOX := true
TW_INCLUDE_FASTBOOTD := true
TW_NO_SCREEN_TIMEOUT := true
TARGET_USES_LOGD := true
TWRP_INCLUDE_LOGCAT := true
