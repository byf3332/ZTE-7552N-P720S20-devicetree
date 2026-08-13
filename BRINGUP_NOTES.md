# Bring-up notes

Last updated: 2026-08-13

## Current status

The device boots Android normally and starts TWRP from `vendor_boot`. The
following recovery paths have been verified on hardware:

- user 0 FBE password decryption and internal storage access
- ADB and MTP
- EROFS logical partition mounting
- USB OTG storage mounting
- reboot to Android, recovery, and bootloader
- fastbootd entry, USB enumeration, and flashing `vendor_boot`
- CPU temperature, battery level, and charging-state reporting

Installation, wipe, and backup are present but have not been exercised on the
device.

## Vendor boot integration

P720S20 has no standalone recovery partition. TWRP is built into
`vendor_boot` while retaining the stock boot-chain layout:

- vendor boot header version 4
- one unnamed `PLATFORM` vendor ramdisk table entry
- legacy LZ4 ramdisk compression
- stock DTB and vendor boot address fields
- stock first-stage ramdisk, fstab variants, platform services, and kernel modules
- TWRP recovery userspace in the same vendor ramdisk

The resulting image is checked against the 104857600-byte partition size and
the device-specific vendor boot header values during the build.

## Storage and decryption

The recovery fstab follows the device's F2FS userdata and metadata-encryption
configuration. User 0 credential decryption uses the device KeyMint,
Gatekeeper, Trusty, and storage-proxy services. Recovery restores the
device-encrypted key state before credential decryption and remounts `/data`
for access to `/data/media/0`.

Logical EROFS partitions use the recovery fs_mgr fstab. USB OTG volumes are
created from Android vold disk events, with the first volume exposed as
`/usb-otg` and subsequent volumes as `/usb-otg-1`, `/usb-otg-2`, and so on.

## Reboot and fastbootd

Reboot handling preserves the Unisoc boot-mode request and BCB command long
enough for LK and recovery init to consume it. Normal Android reboots clear the
stale recovery request, while recovery and fastbootd requests retain their
required BCB state.

Fastbootd uses the recovery fastboot service, the recovery BootControl HAL,
the fs_mgr fstab, and the device Health HAL. Its USB gadget mode has been
verified with a host fastboot connection and a successful `vendor_boot` flash.

## USB behavior

The stock Unisoc configfs flow remains the single owner of the USB gadget.
Recovery supplies compatible FunctionFS descriptors for ADB and MTP. Fastbootd
switches the gadget to fastboot FunctionFS and enumerates as a fastboot device.

## UI behavior

Unsupported recovery-install actions are removed from the Advanced menu.
Single-user decryption state suppresses the redundant `Decrypt Users` action
after user 0 is unlocked. CPU temperature is read from
`/sys/class/thermal/thermal_zone4/temp`.

Screen blanking is classified as Won't Fix for this bring-up. The recovery
keeps screen timeout disabled and the power key opens the lock overlay.

## Stock vendor_boot reference

| Field | Value |
| --- | --- |
| Header version | 4 |
| Page size | 4096 |
| Kernel address | `0x00008000` |
| Ramdisk address | `0x05400000` |
| Tags address | `0x00000100` |
| DTB address | `0x01f00000` |
| Header size | 2128 |
| DTB size | 170052 |
| Vendor cmdline | `console=ttyS1,115200n8 buildvariant=user` |
| Ramdisk table entries | 1 |
| Ramdisk type | `PLATFORM` (1) |
| Ramdisk name | empty |
| Bootconfig size | 0 |
