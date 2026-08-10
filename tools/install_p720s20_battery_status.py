#!/usr/bin/env python3
import sys
from pathlib import Path

target = Path(sys.argv[1])
source = target.read_text()
if "kP720S20OnlinePaths" in source:
    print(f"P720S20 battery online fallback already installed in {target}")
    raise SystemExit(0)

old = """\t\t\tif (cap) {
\t\t\t\tfgets(cap_s, 2, cap);
\t\t\t\tfclose(cap);
\t\t\t\tif (cap_s[0] == 'C')
\t\t\t\t\tcharging = '+';
\t\t\t\telse
\t\t\t\t\tcharging = ' ';
\t\t\t}
"""
new = """\t\t\tif (cap) {
\t\t\t\tfgets(cap_s, 2, cap);
\t\t\t\tfclose(cap);
\t\t\t\tbool power_online = cap_s[0] == 'C';
\t\t\t\tif (!power_online) {
\t\t\t\t\tconst char* kP720S20OnlinePaths[] = {
\t\t\t\t\t\t"/sys/class/power_supply/usb/online",
\t\t\t\t\t\t"/sys/class/power_supply/ac/online",
\t\t\t\t\t};
\t\t\t\t\tfor (const char* path : kP720S20OnlinePaths) {
\t\t\t\t\t\tFILE* online = fopen(path, "rt");
\t\t\t\t\t\tif (online != nullptr) {
\t\t\t\t\t\t\tchar online_s[4] = {};
\t\t\t\t\t\t\tfgets(online_s, sizeof(online_s), online);
\t\t\t\t\t\t\tfclose(online);
\t\t\t\t\t\t\tif (atoi(online_s) > 0) {
\t\t\t\t\t\t\t\tpower_online = true;
\t\t\t\t\t\t\t\tbreak;
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t}
\t\t\t\t}
\t\t\t\tcharging = power_online ? '+' : ' ';
\t\t\t}
"""
n = source.count(old)
if n != 1:
    raise SystemExit(f"unexpected TeamWin battery source state: {n} matches")
target.write_text(source.replace(old, new, 1))
print(f"Installed P720S20 battery online fallback in {target}")
