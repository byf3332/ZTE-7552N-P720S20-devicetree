#!/usr/bin/env python3
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit(f"usage: {sys.argv[0]} REBOOT_C")

target = Path(sys.argv[1])
source = target.read_text()
marker = "P720S20: an argument-less adb reboot must use the normal reboot target"

if marker in source:
    print(f"P720S20 normal adb reboot handling already installed in {target}")
    raise SystemExit(0)

old = '''    if (argc > optind)
        optarg = argv[optind];
    if (!optarg || !optarg[0]) optarg = "shell";
'''
new = f'''    if (argc > optind)
        optarg = argv[optind];
    // {marker}.
    if (!optarg) optarg = "";
'''

count = source.count(old)
if count != 1:
    raise SystemExit(f"unexpected TeamWin reboot.c source state: {count} matches")

target.write_text(source.replace(old, new, 1))
print(f"Installed P720S20 normal adb reboot handling in {target}")