#!/usr/bin/env python3
import sys
from pathlib import Path


def one(source: str, old: str, new: str, name: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"unexpected TeamWin {name} source state: {count} matches"
        )
    return source.replace(old, new, 1)


target = Path(sys.argv[1])
source = target.read_text()
marker = "Fastbootd intentionally skips storage partition setup"
if marker in source:
    print(f"Fastbootd built-in theme handling already installed in {target}")
    raise SystemExit(0)

source = one(
    source,
    "#include <linux/input.h>\n",
    "#include <android-base/properties.h>\n#include <linux/input.h>\n",
    "properties include",
)

old = """\t\ttheme_path = DataManager::GetSettingsStoragePath();
\t\tif (!PartitionManager.Mount_Settings_Storage(false))
\t\t{
\t\t\tint retry_count = 5;
\t\t\twhile (retry_count > 0 && !PartitionManager.Mount_Settings_Storage(false))
\t\t\t{
\t\t\t\tusleep(500000);
\t\t\t\tretry_count--;
\t\t\t}

\t\t\tif (!PartitionManager.Mount_Settings_Storage(true))
\t\t\t{
\t\t\t\tLOGINFO("Unable to mount %s during GUI startup.\\n", theme_path.c_str());
\t\t\t\tcheck = 1;
\t\t\t}
\t\t}

\t\ttheme_path += "theme/ui.zip";
"""
new = """\t\t// Fastbootd intentionally skips storage partition setup. Use the
\t\t// built-in theme without probing settings storage in that mode.
\t\tif (android::base::GetBoolProperty(TW_FASTBOOT_MODE_PROP, false)) {
\t\t\tcheck = 1;
\t\t} else {
\t\t\ttheme_path = DataManager::GetSettingsStoragePath();
\t\t\tif (!PartitionManager.Mount_Settings_Storage(false)) {
\t\t\t\tint retry_count = 5;
\t\t\t\twhile (retry_count > 0 && !PartitionManager.Mount_Settings_Storage(false)) {
\t\t\t\t\tusleep(500000);
\t\t\t\t\tretry_count--;
\t\t\t\t}

\t\t\t\tif (!PartitionManager.Mount_Settings_Storage(true)) {
\t\t\t\t\tLOGINFO("Unable to mount %s during GUI startup.\\n", theme_path.c_str());
\t\t\t\t\tcheck = 1;
\t\t\t\t}
\t\t\t}
\t\t\ttheme_path += "theme/ui.zip";
\t\t}
"""
source = one(source, old, new, "fastbootd theme loading")
target.write_text(source)
print(f"Installed fastbootd built-in theme handling in {target}")
