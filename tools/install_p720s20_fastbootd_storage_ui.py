#!/usr/bin/env python3
import sys
from pathlib import Path


target = Path(sys.argv[1])
source = target.read_text()
marker = "Fastbootd has no recovery backup storage selection"
if marker in source:
    print(f"P720S20 fastbootd storage UI handling already installed in {target}")
    raise SystemExit(0)

old = """\t// This updates the text on all of the storage selection buttons in the GUI
\tDataManager::SetBackupFolder();
"""
new = """\t// Fastbootd has no recovery backup storage selection. Its fstab is parsed
\t// without Setup_Fstab_Partitions(), so no current storage path is selected.
\tif (!android::base::GetBoolProperty(TW_FASTBOOT_MODE_PROP, false))
\t\tDataManager::SetBackupFolder();
"""

count = source.count(old)
if count != 1:
    raise SystemExit(
        f"unexpected TeamWin backup-folder UI source state: {count} matches"
    )

target.write_text(source.replace(old, new, 1))
print(f"Installed P720S20 fastbootd storage UI handling in {target}")
