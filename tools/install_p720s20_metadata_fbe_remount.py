#!/usr/bin/env python3
import sys
from pathlib import Path


if len(sys.argv) != 2:
    raise SystemExit(f"usage: {sys.argv[0]} PARTITIONMANAGER_CPP")

path = Path(sys.argv[1])
text = path.read_text()
marker = "P720S20: restore metadata mapping and DE keys after the UI unmount"

if marker in text:
    print(f"P720S20 metadata/FBE remount fix already installed in {path}")
    raise SystemExit(0)

old = '''#ifdef TW_INCLUDE_FBE
		if (!Mount_By_Path("/data", true)) // /data has to be mounted for FBE
			return -1;

		bool user_need_decrypt = false;'''

new = f'''#ifdef TW_INCLUDE_FBE
		TWPartition* data_partition = Find_Partition_By_Path("/data");
		if (!data_partition) {{
			LOGERR("Unable to locate data partition for FBE decryption\\n");
			return -1;
		}}

		property_get("ro.crypto.fs_crypto_blkdev", crypto_blkdev, "");
		if (crypto_blkdev[0] != '\\0' && TWFunc::Path_Exists(crypto_blkdev)) {{
			// {marker}.
			data_partition->Decrypted_Block_Device = crypto_blkdev;
			data_partition->Is_Decrypted = true;
			LOGINFO("Restored metadata decrypted data block device: '%s'\\n", crypto_blkdev);
		}}

		if (!data_partition->Mount(true)) // /data has to be mounted for FBE
			return -1;

		// Unmounting /data drops the filesystem keyring attached to that
		// superblock. Reinstall the device-encrypted keys before reading the
		// synthetic-password database and verifying the user's credential.
		if (!data_partition->Decrypt_FBE_DE()) {{
			LOGERR("Unable to restore FBE device-encrypted keys after mounting /data\\n");
			return -1;
		}}

		// Keystore2 starts before metadata-encrypted /data is available and
		// initially opens an empty recovery database. Reload the real Android
		// database after DE keys make it readable, so locksettings keys and
		// their blobs remain available for Synthetic Password decryption.
		property_set("ctl.stop", "keystore2");
		char keystore_state[PROPERTY_VALUE_MAX];
		for (int retry = 0; retry < 50; ++retry) {{
			property_get("init.svc.keystore2", keystore_state, "");
			if (strcmp(keystore_state, "stopped") == 0) break;
			usleep(100000);
		}}
		property_get("init.svc.keystore2", keystore_state, "");
		if (strcmp(keystore_state, "stopped") != 0) {{
			LOGERR("Timed out stopping Keystore2 before database reload\\n");
			return -1;
		}}
		int keystore_copy_result =
			TWFunc::Exec_Cmd("cp /data/misc/keystore/persistent.sqlite "
						"/tmp/misc/keystore/persistent.sqlite && "
						"chown root:keystore /tmp/misc/keystore/persistent.sqlite && "
						"chmod 0660 /tmp/misc/keystore/persistent.sqlite");
		property_set("ctl.start", "keystore2");
		for (int retry = 0; retry < 50; ++retry) {{
			property_get("init.svc.keystore2", keystore_state, "");
			if (strcmp(keystore_state, "running") == 0) break;
			usleep(100000);
		}}
		property_get("init.svc.keystore2", keystore_state, "");
		if (strcmp(keystore_state, "running") != 0) {{
			LOGERR("Timed out restarting Keystore2 after database reload\\n");
			return -1;
		}}
		if (keystore_copy_result != 0) {{
			LOGERR("Unable to reload the Android Keystore2 database\\n");
			return -1;
		}}

		bool user_need_decrypt = false;'''

count = text.count(old)
if count != 1:
    raise SystemExit(
        f"unexpected TeamWin Decrypt_Device FBE source state: {count} matches"
    )

path.write_text(text.replace(old, new, 1))
print(f"Installed P720S20 metadata/FBE remount fix in {path}")
