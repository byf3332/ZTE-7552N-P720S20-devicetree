# Bring-up notes

## Corrections made to the twrpdtgen output

The generator was fed a `vendor_boot` image and produced several assumptions
that fit older A/B recovery layouts better than this device. This revision:

- removes `BOARD_USES_RECOVERY_AS_BOOT := true`
- removes the fake 100 MiB `BOARD_RECOVERYIMAGE_PARTITION_SIZE`
- replaces the fake 100 MiB boot size with the observed 64 MiB boot partition size
- removes the nonexistent `prebuilt/kernel` reference
- sets `BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE := 104857600`
- uses `BOARD_BOOT_HEADER_VERSION := 4`
- restores the stock vendor-boot address fields and vendor cmdline
- uses legacy LZ4 for the vendor ramdisk
- removes generator hardcoded `super` group sizes rather than guessing them
- fixes userdata filesystem type to F2FS
- restores the stock `/data` FBE metadata in the TWRP fstab
- adds `vendor_boot`, `init_boot` and `super` to the TWRP fstab
- preserves stock first-stage files and all stock recovery kernel modules
- keeps the stock Unisoc USB configfs init and disables TWRP's default USB init to avoid two owners of the same gadget
- moves the standard GSI AVB public keys into vendor_boot as required by the generic-ramdisk/no-recovery layout
- uses a `twrp_P720S20` product instead of the legacy `omni_P720S20` product

## Important stock vendor_boot v4 fields

Expected values from the supplied stock image:

| field | value |
|---|---|
| header version | 4 |
| page size | 4096 |
| kernel address | `0x00008000` |
| ramdisk address | `0x05400000` |
| tags address | `0x00000100` |
| DTB address | `0x01f00000` |
| header size | 2128 |
| DTB size | 170052 |
| vendor cmdline | `console=ttyS1,115200n8 buildvariant=user` |
| ramdisk table entries | 1 |
| ramdisk type | PLATFORM (1) |
| ramdisk name | empty |
| bootconfig size | 0 |

The checker under `tools/` validates these fields on the first build.

## Do not add for the first build

`BOARD_INCLUDE_RECOVERY_RAMDISK_IN_VENDOR_BOOT := true`

That flag would create a distinct recovery ramdisk fragment. The supplied stock
P720S20 image has only the default PLATFORM vendor ramdisk, and the first-pass
tree intentionally mirrors that layout.

Also do not restore the generator's hardcoded `BOARD_SUPER_PARTITION_SIZE`
until an exact partition-table value is intentionally supplied.
