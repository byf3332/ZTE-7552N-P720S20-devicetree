#!/usr/bin/env python3
import re
import sys
from pathlib import Path


def replace_one(text: str, old: str, new: str, name: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"unexpected TeamWin {name} source state: {count} matches")
    return text.replace(old, new, 1)


if len(sys.argv) != 3:
    raise SystemExit(f"usage: {sys.argv[0]} FSCRYPT_CPP DECRYPT_CPP")

fscrypt_path = Path(sys.argv[1])
fscrypt = fscrypt_path.read_text()
fstab_marker = "P720S20: use the Android-format fstab dedicated to vold"
if fstab_marker not in fscrypt:
    fscrypt = replace_one(
        fscrypt,
        '''        if (!ReadDefaultFstab(&fstab_default)) {
            PLOG(ERROR) << "Failed to open default fstab";
            return false;
        }''',
        f'''        // {fstab_marker}.
        if (!ReadFstabFromFile("/system/etc/p720s20.crypto.fstab", &fstab_default)) {{
            PLOG(ERROR) << "Failed to open P720S20 crypto fstab";
            return false;
        }}''',
        "crypto fstab selection",
    )
    fscrypt_path.write_text(fscrypt)
    print(f"Installed P720S20 vold fstab selection in {fscrypt_path}")
else:
    print(f"P720S20 vold fstab selection already installed in {fscrypt_path}")

decrypt_path = Path(sys.argv[2])
decrypt = decrypt_path.read_text()
unwrap_marker = "P720S20: collect Unisoc KeyMint output from update and finish"
if unwrap_marker not in decrypt:
    decrypt, count = re.subn(
        r'''[ \t]*::keystore::hidl_vec<uint8_t> cipher_text_hidlvec;\n\n[ \t]*cipher_text_hidlvec\.setToExternal\(cipher_text, spblob_data\.size\(\) - 14 /\* 1 each for version and SYNTHETIC_PASSWORD_PASSWORD_BASED and 12 for the iv \*/\);\n''',
        "",
        decrypt,
        count=1,
    )
    if count != 1:
        raise SystemExit("unexpected TeamWin obsolete finish-input buffer source state")

    pattern = r'''[ \t]*std::optional<std::vector<uint8_t>> optPlaintext;\n\n[ \t]*begin_rc = encOperationResponse\.iOperation->finish\(cipher_text_hidlvec, \{\}, &optPlaintext\);\n[ \t]*if \(!begin_rc\.isOk\(\)\) \{\n[ \t]*printf\("finish reponse failed"\);\n[ \t]*return disk_decryption_secret_key;\n[ \t]*\}\n\n[ \t]*size_t keystore_result_size = optPlaintext->size\(\);'''
    replacement = f'''            if (!encOperationResponse.iOperation) {{
                printf("KeyMint createOperation returned no operation\\n");
                return disk_decryption_secret_key;
            }}

            // {unwrap_marker}.
            std::vector<uint8_t> cipher_input(cipher_text,
                                               cipher_text + spblob_data.size() - 14);
            std::optional<std::vector<uint8_t>> update_plaintext;
            auto update_rc = encOperationResponse.iOperation->update(cipher_input,
                                                                      &update_plaintext);
            if (!update_rc.isOk()) {{
                printf("KeyMint update failed: %s\\n", update_rc.getDescription().c_str());
                return disk_decryption_secret_key;
            }}
            std::optional<std::vector<uint8_t>> finish_plaintext;
            auto finish_rc = encOperationResponse.iOperation->finish(
                std::nullopt, std::nullopt, &finish_plaintext);
            if (!finish_rc.isOk()) {{
                printf("KeyMint finish failed: %s\\n", finish_rc.getDescription().c_str());
                return disk_decryption_secret_key;
            }}
            std::vector<uint8_t> plaintext;
            if (update_plaintext) plaintext.insert(plaintext.end(), update_plaintext->begin(), update_plaintext->end());
            if (finish_plaintext) plaintext.insert(plaintext.end(), finish_plaintext->begin(), finish_plaintext->end());
            if (plaintext.size() <= 28) {{
                printf("KeyMint returned an invalid synthetic password plaintext size: %zu\\n", plaintext.size());
                return disk_decryption_secret_key;
            }}
            size_t keystore_result_size = plaintext.size();'''
    # A replacement callback preserves C++ escape sequences such as "\\n".
    # Passing the string directly to re.subn() would interpret backslashes a
    # second time and emit invalid multi-line C++ string literals.
    decrypt, count = re.subn(
        pattern, lambda _match: replacement, decrypt, count=1
    )
    if count != 1:
        raise SystemExit("unexpected TeamWin KeyMint finish source state")

    decrypt, count = re.subn(
        r'memcpy\(keystore_result, &optPlaintext->front\(\), keystore_result_size\);',
        'memcpy(keystore_result, plaintext.data(), keystore_result_size);',
        decrypt,
        count=1,
    )
    if count != 1:
        raise SystemExit("unexpected TeamWin KeyMint plaintext copy source state")
    decrypt_path.write_text(decrypt)
    print(f"Installed P720S20 synthetic-password unwrap compatibility in {decrypt_path}")
else:
    print(f"P720S20 synthetic-password unwrap compatibility already installed in {decrypt_path}")
