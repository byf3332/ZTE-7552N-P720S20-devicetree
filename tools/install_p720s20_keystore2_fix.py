#!/usr/bin/env python3
import sys
from pathlib import Path


def replace_one(text: str, old: str, new: str, name: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"unexpected TeamWin {name} source state: {count} matches")
    return text.replace(old, new, 1)


if len(sys.argv) != 4:
    raise SystemExit(f"usage: {sys.argv[0]} KEYMASTER_CPP KEYMASTER_H KEYSTORAGE_CPP")

cpp_path = Path(sys.argv[1])
cpp = cpp_path.read_text()
cpp_marker = "P720S20: do not abort a Keystore2 operation after finish"
if cpp_marker not in cpp:
    cpp = replace_one(
        cpp,
        """KeymasterOperation::~KeymasterOperation() {
    if (ks2Operation) ks2Operation->abort();
}""",
        f"""KeymasterOperation::~KeymasterOperation() {{
    // {cpp_marker}.
    if (ks2Operation && !operationFinished) ks2Operation->abort();
}}""",
        "KeymasterOperation destructor",
    )
    cpp = replace_one(
        cpp,
        """    auto rc = ks2Operation->finish(std::nullopt, std::nullopt, &out_vec);
    if (logKeystore2ExceptionIfPresent(rc, "finish")) {
        ks2Operation = nullptr;
        return false;
    }

    if (output) *output = std::string(out_vec->begin(), out_vec->end());

    return true;
}""",
        """    auto rc = ks2Operation->finish(std::nullopt, std::nullopt, &out_vec);
    operationFinished = true;
    if (logKeystore2ExceptionIfPresent(rc, "finish")) return false;

    if (output) {
        if (!out_vec) {
            LOG(ERROR) << "finish returned no output";
            return false;
        }
        *output = std::string(out_vec->begin(), out_vec->end());
    }

    return true;
}""",
        "KeymasterOperation::finish",
    )
    cpp_path.write_text(cpp)
    print(f"Installed P720S20 Keystore2 operation lifecycle fix in {cpp_path}")
else:
    print(f"P720S20 Keystore2 operation lifecycle fix already installed in {cpp_path}")

header_path = Path(sys.argv[2])
header = header_path.read_text()
header_marker = "P720S20 finished-operation state"
if header_marker not in header:
    header = replace_one(
        header,
        """    explicit operator bool() const { return (bool)ks2Operation; }""",
        """    explicit operator bool() const { return (bool)ks2Operation && !operationFinished; }""",
        "KeymasterOperation validity",
    )
    header = replace_one(
        header,
        """        errorCode = rhs.errorCode;
        rhs.errorCode = km::ErrorCode::UNKNOWN_ERROR;

        return *this;""",
        """        errorCode = rhs.errorCode;
        rhs.errorCode = km::ErrorCode::UNKNOWN_ERROR;

        operationFinished = rhs.operationFinished;
        rhs.operationFinished = true;

        return *this;""",
        "KeymasterOperation move assignment",
    )
    header = replace_one(
        header,
        """    km::ErrorCode errorCode;
    DISALLOW_COPY_AND_ASSIGN(KeymasterOperation);""",
        f"""    km::ErrorCode errorCode;
    // {header_marker}.
    bool operationFinished = false;
    DISALLOW_COPY_AND_ASSIGN(KeymasterOperation);""",
        "KeymasterOperation state",
    )
    header_path.write_text(header)
    print(f"Installed P720S20 Keystore2 finished-operation state in {header_path}")
else:
    print(f"P720S20 Keystore2 finished-operation state already installed in {header_path}")

storage_path = Path(sys.argv[3])
storage = storage_path.read_text()
storage_marker = "P720S20: retain an existing blob when KeyMint did not upgrade it"
if storage_marker not in storage:
    storage = replace_one(
        storage,
        """    // If key blob wasn't upgraded, nothing left to do.
    // if (!opHandle.getUpgradedBlob()) return opHandle;
""",
        f"""    // {storage_marker}.
    if (!opHandle.getUpgradedBlob()) return opHandle;
""",
        "KeyStorage upgraded blob handling",
    )
    storage_path.write_text(storage)
    print(f"Installed P720S20 upgraded key blob guard in {storage_path}")
else:
    print(f"P720S20 upgraded key blob guard already installed in {storage_path}")

checkpoint_marker = "P720S20: recovery has no vold checkpoint lifecycle"
storage = storage_path.read_text()
if checkpoint_marker not in storage:
    storage = replace_one(
        storage,
        """    if (cp_needsCheckpoint()) {""",
        f"""    // {checkpoint_marker}; commit upgraded blobs immediately.
    if (false) {{""",
        "KeyStorage checkpoint handling",
    )
    storage_path.write_text(storage)
    print(f"Installed P720S20 recovery checkpoint bypass in {storage_path}")
else:
    print(f"P720S20 recovery checkpoint bypass already installed in {storage_path}")
