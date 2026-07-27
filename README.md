# TWRP device tree — ZTE 7552N / P720S20

First bring-up tree for **ZTE 7552N (P720S20 / ums9620_2h10)**, based on the
`twrpdtgen 3.0.0` output and the stock `vendor_boot_a.img` vendor ramdisk.

## Stock layout used by this tree

- Android 13
- platform: `ums9620`
- board: `ums9620_2h10`
- no standalone `recovery` partition
- recovery userspace is in `vendor_boot`
- `vendor_boot` header v4, 4096-byte page size
- `vendor_boot` partition size: 104857600 bytes
- one vendor-ramdisk-table entry, type `PLATFORM`
- no separate `RECOVERY` or `DLKM` vendor-ramdisk fragment
- stock vendor ramdisk compression: legacy LZ4
- stock DTB size: 170052 bytes
- stock DTB address: `0x01f00000`

For that reason this tree uses
`BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true`, but intentionally does
**not** set `BOARD_INCLUDE_RECOVERY_RAMDISK_IN_VENDOR_BOOT`.

## Stock pieces preserved

The tree carries the stock:

- `first_stage_ramdisk/` including all four UMS9620 fstab variants and fsck/snapuserd support
- `/lib/modules` with `modules.load` and `modules.load.recovery`
- Unisoc `init.recovery.common.rc`
- UMS9620 ueventd rc files
- stock recovery `servicemanager.recovery.rc` and `snapuserd.rc`
- stock Unisoc configfs USB setup (`TW_EXCLUDE_DEFAULT_USB_INIT := true`)
- DTB extracted from stock `vendor_boot`

It does **not** copy the stock recovery executable or the complete stock
`/system` recovery userspace over TWRP.

## Build

Use the TWRP AOSP 12.1 manifest and place this directory at:

`device/zte/P720S20`

Then:

```sh
source build/envsetup.sh
lunch twrp_P720S20-eng
mka vendorbootimage
```

Expected output:

`out/target/product/P720S20/vendor_boot.img`

Before any device-side test, run:

```sh
python3 device/zte/P720S20/tools/check_vendor_boot.py out/target/product/P720S20/vendor_boot.img
```

The first milestone is a structurally correct `vendor_boot` that reaches TWRP
with display, touch and ADB. FBE `/data` decryption is enabled in the build
configuration but remains a later runtime validation item.
