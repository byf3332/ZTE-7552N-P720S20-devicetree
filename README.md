# TWRP device tree for ZTE 7552N / P720S20

This repository contains the TeamWin Recovery Project device tree for the
ZTE 7552N (`P720S20`, `ums9620_2h10`).

## Status

**Testing**

The tree builds a TWRP 12.1 `vendor_boot` image. Device functionality is still
being validated.

## Device specifications

| Component | Value |
| --- | --- |
| Device | ZTE 7552N |
| Product | P720S20 |
| Platform | Unisoc UMS9620 |
| Board | ums9620_2h10 |
| Android version | Android 13 |
| Architecture | arm64 |
| Partition scheme | A/B |
| Recovery location | `vendor_boot` |
| Vendor boot header | Version 4 |
| Vendor boot partition size | 104857600 bytes |
| Vendor ramdisk compression | Legacy LZ4 |

## Boot image layout

The device has no standalone recovery partition. Recovery resources are stored
in `vendor_boot` using the stock layout:

- one vendor ramdisk table entry of type `PLATFORM`
- no separate `RECOVERY` vendor ramdisk fragment
- no separate `DLKM` vendor ramdisk fragment
- generic kernel image boot flow
- stock device tree blob

The corresponding build configuration uses:

```make
BOARD_USES_GENERIC_KERNEL_IMAGE := true
BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true
TARGET_NO_RECOVERY := true
```

`BOARD_INCLUDE_RECOVERY_RAMDISK_IN_VENDOR_BOOT` is left unset to preserve the
single-`PLATFORM` vendor ramdisk layout.

## Implementation

The vendor ramdisk is constructed from the stock platform ramdisk and the TWRP
recovery root.

The tree includes build-time handling for:

- stock first-stage ramdisk files and fstab variants
- stock kernel modules and recovery module load list
- Virtual A/B and `snapuserd` support
- Unisoc recovery init and ueventd configuration
- first-stage fstab preparation
- ramdisk file permission metadata
- TWRP recovery SELinux policy and contexts
- Unisoc configfs USB setup
- Unisoc DRM/KMS display support
- ext4, F2FS, EROFS and VFAT filesystems
- fastbootd and recovery repacking tools
- Android FBE and metadata encryption support

The display build hook installs TeamWin's generic DRM/KMS backend before
`libminuitwrp` is compiled. The backend uses standard KMS CRTC and page-flip
operations suitable for the device's `sprd-drm` driver.
