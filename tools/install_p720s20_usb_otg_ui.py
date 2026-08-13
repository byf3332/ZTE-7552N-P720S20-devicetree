#!/usr/bin/env python3
import sys
from pathlib import Path


def one(source: str, old: str, new: str, name: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"unexpected TeamWin {name} source state: {count} matches")
    return source.replace(old, new, 1)


partition = Path(sys.argv[1])
manager = Path(sys.argv[2])

partition_source = partition.read_text()
manager_source = manager.read_text()

partition_source = one(
    partition_source,
    """\t\tIs_Storage = true;
\t\tRemovable = true;
\t\tWipe_Available_in_GUI = true;
\t\tWildcard_Block_Device = true;
""",
    """\t\t// Keep the P720S20 USB controller entry as a hotplug discovery
\t\t// object. Actual storage partitions are added after its disk uevent.
\t\tIs_Storage = Mount_Point != "/usb-otg";
\t\tRemovable = true;
\t\tWipe_Available_in_GUI = Mount_Point != "/usb-otg";
\t\tWildcard_Block_Device = true;
""",
    "sysfs storage placeholder",
)

partition_source = one(
    partition_source,
    """bool TWPartition::Find_Wildcard_Block_Devices(const string& Device) {
\tint mount_point_index = 0; // we will need to create separate mount points for each partition found and we use this index to name each one
""",
    """bool TWPartition::Find_Wildcard_Block_Devices(const string& Device) {
\tint mount_point_index = 0; // we will need to create separate mount points for each partition found and we use this index to name each one
\tstring storage_mount_point = Mount_Point;
\tif (!Sysfs_Entry.empty() && (Mount_Point == "/usb-otg" || Mount_Point == "/usb-otg-sysfs")) {
\t\tMount_Point = "/usb-otg-sysfs";
\t\tstorage_mount_point = "/usb-otg";
\t}
""",
    "dynamic storage mount-point setup",
)

partition_source = one(
    partition_source,
    """\t\tTWPartition *part = new TWPartition;
\t\tchar buffer[MAX_FSTAB_LINE_LENGTH];
\t\tsprintf(buffer, "%s %s-%i auto defaults defaults", item.c_str(), Mount_Point.c_str(), ++mount_point_index);
\t\tpart->Process_Fstab_Line(buffer, false, NULL);
""",
    """\t\tTWPartition *part = new TWPartition;
\t\tchar buffer[MAX_FSTAB_LINE_LENGTH];
\t\t++mount_point_index;
\t\tif (mount_point_index == 1)
\t\t\tsprintf(buffer, "%s %s auto defaults defaults", item.c_str(), storage_mount_point.c_str());
\t\telse
\t\t\tsprintf(buffer, "%s %s-%i auto defaults defaults", item.c_str(), storage_mount_point.c_str(), mount_point_index - 1);
\t\tpart->Process_Fstab_Line(buffer, false, NULL);
""",
    "dynamic storage mount point",
)

partition_source = one(
    partition_source,
    """\t\tchar display[MAX_FSTAB_LINE_LENGTH];
\t\tsprintf(display, "%s %i", Storage_Name.c_str(), mount_point_index);
\t\tpart->Storage_Name = display;
\t\tpart->Display_Name = display;
""",
    """\t\tchar display[MAX_FSTAB_LINE_LENGTH];
\t\tif (mount_point_index == 1)
\t\t\tsprintf(display, "%s", Storage_Name.c_str());
\t\telse
\t\t\tsprintf(display, "%s %i", Storage_Name.c_str(), mount_point_index - 1);
\t\tpart->Storage_Name = display;
\t\tpart->Display_Name = display;
""",
    "dynamic storage display name",
)

partition_source = one(
    partition_source,
    "\t\tpart->Is_Storage = Is_Storage;\n",
    "\t\tpart->Is_Storage = true;\n",
    "dynamic storage classification",
)

manager_source = one(
    manager_source,
    """\tTranslate_Partition("/usb-otg", "usbotg", "USB OTG", "usbotg", "USB OTG");
\tTranslate_Partition("/sd-ext", "sdext", "SD-EXT");
""",
    """\tTranslate_Partition("/usb-otg", "usbotg", "USB OTG", "usbotg", "USB OTG");
\tTWPartition* usb_otg = PartitionManager.Find_Partition_By_Path("/usb-otg");
\tif (usb_otg)
\t\tusb_otg->Storage_Name = gui_lookup("usbotg", "USB OTG");
\tTranslate_Partition("/sd-ext", "sdext", "SD-EXT");
""",
    "USB OTG translation",
)

manager_source = one(
    manager_source,
    """\t\tif (!(*sysfs)->Sysfs_Entry.empty()) {
\t\t\tTranslate_Partition((*sysfs)->Mount_Point.c_str(), "autostorage", "Storage", "autostorage", "Storage");
\t\t}
""",
    """\t\tif (!(*sysfs)->Sysfs_Entry.empty() && (*sysfs)->Mount_Point != "/usb-otg") {
\t\t\tTranslate_Partition((*sysfs)->Mount_Point.c_str(), "autostorage", "Storage", "autostorage", "Storage");
\t\t}
""",
    "generic sysfs translation",
)

partition.write_text(partition_source)
manager.write_text(manager_source)
print(f"Installed P720S20 USB OTG UI handling in {partition} and {manager}")
