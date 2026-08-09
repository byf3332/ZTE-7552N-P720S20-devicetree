#!/usr/bin/env python3

import hashlib
import sys
from pathlib import Path

EXPECTED_SOURCE_SHA256 = (
    "8d5a7f23322031f106ae357c62d9f038b02b2f9f6107fa10e7c3c271aebf8260"
)

ATOMIC_BACKEND_MARKERS = (
    b"#define DEFAULT_NUM_LMS 2",
    b"mode_properties",
    b"drmModeAtomicCommit",
)

GENERIC_BACKEND_MARKERS = (
    b"drmModeSetCrtc",
    b"drmModePageFlip",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            f"usage: {sys.argv[0]} GENERIC_BACKEND UPSTREAM_BACKEND"
        )

    source_path = Path(sys.argv[1])
    target_path = Path(sys.argv[2])

    if not source_path.is_file():
        raise SystemExit(f"generic DRM backend is missing: {source_path}")

    if not target_path.is_file():
        raise SystemExit(f"TeamWin DRM backend is missing: {target_path}")

    source = source_path.read_bytes()
    source_hash = sha256(source)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise SystemExit(
            "unexpected generic DRM backend SHA-256: "
            f"{source_hash}"
        )

    target = target_path.read_bytes()
    if target == source:
        print(
            "TeamWin generic DRM backend already installed: "
            f"{target_path}"
        )
        return

    missing = [
        marker.decode("ascii")
        for marker in ATOMIC_BACKEND_MARKERS
        if marker not in target
    ]
    if missing:
        raise SystemExit(
            "unexpected TeamWin 12.1 DRM backend; missing markers: "
            + ", ".join(missing)
        )

    if not all(marker in source for marker in GENERIC_BACKEND_MARKERS):
        raise SystemExit("generic DRM backend is missing required KMS calls")

    target_path.write_bytes(source)

    installed = target_path.read_bytes()
    if sha256(installed) != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"failed to install generic DRM backend: {target_path}")

    print(
        "Installed TeamWin generic DRM backend for Unisoc sprd-drm: "
        f"{target_path}"
    )


if __name__ == "__main__":
    main()
