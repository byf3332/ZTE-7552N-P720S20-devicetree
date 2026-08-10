#!/usr/bin/env python3
import sys
from pathlib import Path


def replace_one(text: str, old: str, new: str, name: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"unexpected TeamWin {name} source state: {count} matches")
    return text.replace(old, new, 1)


if len(sys.argv) != 3:
    raise SystemExit(f"usage: {sys.argv[0]} KEYMASTER_CPP KEYSTORAGE_CPP")

keymaster_path = Path(sys.argv[1])
keymaster = keymaster_path.read_text()
keymaster_marker = "P720S20: a finished Keystore2 operation must not be aborted"
if keymaster_marker not in keymaster:
    keymaster = replace_one(
        keymaster,
        """    if (output) *output = std::string(out_vec->begin(), out_vec->end());

    return true;
}""",
        f"""    if (output) {{
        if (!out_vec) {{
            LOG(ERROR) << \"finish returned no output\";
            ks2Operation = nullptr;
            return false;
        }}
        *output = std::string(out_vec->begin(), out_vec->end());
    }}

    // {keymaster_marker}.
    ks2Operation = nullptr;
    return true;
}}""",
        "KeymasterOperation::finish",
    )
    keymaster_path.write_text(keymaster)
    print(f"Installed P720S20 Keystore2 operation lifecycle fix in {keymaster_path}")
else:
    print(f"P720S20 Keystore2 operation lifecycle fix already installed in {keymaster_path}")

keystorage_path = Path(sys.argv[2])
keystorage = keystorage_path.read_text()
keystorage_marker = "P720S20: retain an existing blob when KeyMint did not upgrade it"
if keystorage_marker not in keystorage:
    keystorage = replace_one(
        keystorage,
        """    // If key blob wasn't upgraded, nothing left to do.
    // if (!opHandle.getUpgradedBlob()) return opHandle;
""",
        f"""    // {keystorage_marker}.
    if (!opHandle.getUpgradedBlob()) return opHandle;
""",
        "KeyStorage upgraded blob handling",
    )
    keystorage_path.write_text(keystorage)
    print(f"Installed P720S20 upgraded key blob guard in {keystorage_path}")
else:
    print(f"P720S20 upgraded key blob guard already installed in {keystorage_path}")