#!/usr/bin/env python3
import sys
from pathlib import Path

def one(s, old, new, name):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"unexpected TeamWin {name} source state: {n} matches")
    return s.replace(old, new, 1)

target = Path(sys.argv[1])
s = target.read_text()
if "WriteP720S20BootloaderMessage" in s:
    print(f"P720S20 BCB reboot handling already installed in {target}")
    raise SystemExit(0)

s = one(s, """#include <sys/reboot.h>
#include <sys/sendfile.h>
""", """#include <sys/reboot.h>
#include <sys/syscall.h>
#include <sys/sendfile.h>
""", "reboot syscall include")

s = one(s, """void TWFunc::Clear_Bootloader_Message() {
\tstd::string err;
\tif (!clear_bootloader_message(&err)) {
\t\tLOGINFO("%s\\n", err.c_str());
\t}
}
""", """namespace {
constexpr const char* kP720S20MiscDevice = "/dev/block/by-name/misc";

bool WriteP720S20BootloaderMessage(const char* command, const char* recovery) {
\tbootloader_message boot = {};
\tif (command != nullptr)
\t\tsnprintf(boot.command, sizeof(boot.command), "%s", command);
\tif (recovery != nullptr)
\t\tsnprintf(boot.recovery, sizeof(boot.recovery), "%s", recovery);
\tstd::string err;
\tif (!write_bootloader_message_to(boot, kP720S20MiscDevice, &err)) {
\t\tLOGINFO("Unable to write P720S20 BCB: %s\\n", err.c_str());
\t\treturn false;
\t}
\tsync();
\treturn true;
}
}  // namespace

void TWFunc::Clear_Bootloader_Message() {
\tWriteP720S20BootloaderMessage("", "");
}
""", "Clear_Bootloader_Message")

s = one(s, """\t\tcase rb_current:
\t\tcase rb_system:
\t\t\tUpdate_Intent_File("s");
\t\t\tsync();
\t\t\tcheck_and_run_script("/system/bin/rebootsystem.sh", "reboot system");
#ifdef ANDROID_RB_PROPERTY
\t\t\treturn property_set(ANDROID_RB_PROPERTY, "reboot,");
#elif defined(ANDROID_RB_RESTART)
\t\t\treturn android_reboot(ANDROID_RB_RESTART, 0, 0);
#else
\t\t\treturn reboot(RB_AUTOBOOT);
#endif
""", """\t\tcase rb_current:
\t\tcase rb_system:
\t\t\tUpdate_Intent_File("s");
\t\t\tif (!WriteP720S20BootloaderMessage("", ""))
\t\t\t\treturn -1;
\t\t\tcheck_and_run_script("/system/bin/rebootsystem.sh", "reboot system");
\t\t\treturn property_set(ANDROID_RB_PROPERTY, "reboot,");
""", "system reboot")

s = one(s, """\t\tcase rb_recovery:
\t\t\tcheck_and_run_script("/system/bin/rebootrecovery.sh", "reboot recovery");
\t\t\treturn property_set(ANDROID_RB_PROPERTY, "reboot,recovery");
\t\tcase rb_bootloader:
\t\t\tcheck_and_run_script("/system/bin/rebootbootloader.sh", "reboot bootloader");
\t\t\treturn property_set(ANDROID_RB_PROPERTY, "reboot,bootloader");
""", """\t\tcase rb_recovery:
\t\t\tif (!WriteP720S20BootloaderMessage("boot-recovery", "recovery\\n"))
\t\t\t\treturn -1;
\t\t\tcheck_and_run_script("/system/bin/rebootrecovery.sh", "reboot recovery");
\t\t\treturn property_set(ANDROID_RB_PROPERTY, "reboot,");
\t\tcase rb_bootloader:
\t\t\tif (!WriteP720S20BootloaderMessage("", ""))
\t\t\t\treturn -1;
\t\t\tcheck_and_run_script("/system/bin/rebootbootloader.sh", "reboot bootloader");
\t\t\treturn syscall(__NR_reboot, LINUX_REBOOT_MAGIC1, LINUX_REBOOT_MAGIC2,
\t\t\t                  LINUX_REBOOT_CMD_RESTART2,
\t\t\t                  const_cast<char*>("bootloader"));
""", "recovery and bootloader reboot")

s = one(s, """\t\tcase rb_fastboot:
\t\t\treturn property_set(ANDROID_RB_PROPERTY, "reboot,fastboot");
""", """\t\tcase rb_fastboot:
\t\t\tif (!WriteP720S20BootloaderMessage("boot-fastboot", ""))
\t\t\t\treturn -1;
\t\t\treturn property_set(ANDROID_RB_PROPERTY, "reboot,fastboot");
""", "fastbootd reboot")

target.write_text(s)
print(f"Installed P720S20 direct BCB reboot handling in {target}")
