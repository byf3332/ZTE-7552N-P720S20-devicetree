# TWRP for ZTE 7552N / P720S20

TeamWin Recovery Project 12.1 device tree for the ZTE 7552N (`P720S20`,
`ums9620_2h10`) running Android 13.

## Current build

[Release 31693837609](https://github.com/byf3332/Lazy_Action-Recoverys-Builder/releases/tag/31693837609)

## Device information

| Item | Value |
| --- | --- |
| Device | ZTE 7552N |
| Product | P720S20 |
| Platform | Unisoc UMS9620 |
| Board | ums9620_2h10 |
| Android version | Android 13 |
| Architecture | arm64 |
| Partition scheme | A/B with compressed Virtual A/B |
| Recovery image | `vendor_boot` |
| Vendor boot header | Version 4 |
| Vendor boot partition size | 104857600 bytes |
| Vendor ramdisk compression | Legacy LZ4 |

## Verified functionality

- Normal Android boot
- TWRP recovery startup
- User 0 FBE password decryption
- Internal storage access
- Recovery ADB access
- USB OTG storage mounting
- MTP file transfer
- EROFS logical partition mounting
- Reboot to Android, recovery, and bootloader
- Fastbootd support
- CPU temperature reporting
- Battery level and charging-state reporting

## Not verified functions

These functions are available but have not been tested on the device:

- Installation
- Wipe
- Backup

## Vendor boot layout

The device has no standalone recovery partition. Recovery resources are stored
in `vendor_boot` using the stock layout:

- one `PLATFORM` vendor ramdisk table entry
- generic kernel image boot flow
- stock device tree blob
