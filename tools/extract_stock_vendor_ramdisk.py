#!/usr/bin/env python3
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path


def align4(value):
    return (value + 3) & ~3


def output_path(root, name):
    if name.startswith('/'):
        raise ValueError(f'absolute path in stock ramdisk: {name}')

    parts = Path(name).parts
    if not parts or any(part in ('', '..') for part in parts):
        raise ValueError(f'unsafe path in stock ramdisk: {name}')

    path = root.joinpath(*parts)

    current = root
    for part in parts[:-1]:
        current /= part
        if current.is_symlink():
            raise ValueError(f'symlink parent in stock ramdisk: {name}')

    return path


def replace_path(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def extract_newc(data, root):
    offset = 0
    count = 0

    while True:
        offset = align4(offset)

        if offset + 110 > len(data):
            raise ValueError('truncated newc header')

        header = data[offset:offset + 110]
        offset += 110

        if header[:6] not in (b'070701', b'070702'):
            raise ValueError(f'bad newc magic at 0x{offset - 110:x}')

        fields = [
            int(header[6 + i * 8:14 + i * 8], 16)
            for i in range(13)
        ]

        mode = fields[1]
        mtime = fields[5]
        size = fields[6]
        name_size = fields[11]

        if offset + name_size > len(data):
            raise ValueError('truncated newc filename')

        raw_name = data[offset:offset + name_size]
        offset = align4(offset + name_size)

        if not raw_name.endswith(b'\0'):
            raise ValueError('unterminated newc filename')

        name = raw_name[:-1].decode('utf-8', 'surrogateescape')

        if name == 'TRAILER!!!':
            break

        if offset + size > len(data):
            raise ValueError(f'truncated newc payload: {name}')

        payload = data[offset:offset + size]
        offset = align4(offset + size)

        path = output_path(root, name)
        path.parent.mkdir(parents=True, exist_ok=True)

        file_type = stat.S_IFMT(mode)
        permissions = stat.S_IMODE(mode)

        if file_type == stat.S_IFDIR:
            if path.is_symlink() or (path.exists() and not path.is_dir()):
                replace_path(path)
            path.mkdir(parents=True, exist_ok=True)
            os.chmod(path, permissions)

        elif file_type == stat.S_IFREG:
            replace_path(path)
            path.write_bytes(payload)
            os.chmod(path, permissions)

        elif file_type == stat.S_IFLNK:
            replace_path(path)
            os.symlink(
                payload.decode('utf-8', 'surrogateescape'),
                path,
            )

        else:
            raise ValueError(
                f'unsupported file type {file_type:#o}: {name}'
            )

        if not path.is_symlink():
            os.utime(
                path,
                (mtime, mtime),
                follow_symlinks=False,
            )

        count += 1

    return count


def main():
    if len(sys.argv) != 4:
        raise SystemExit(
            f'usage: {sys.argv[0]} '
            'STOCK_VENDOR_RAMDISK_LZ4 OUTPUT_DIR LZ4_TOOL'
        )

    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    lz4_tool = Path(sys.argv[3])

    if not lz4_tool.is_file() or not os.access(lz4_tool, os.X_OK):
        raise SystemExit(f'lz4 tool is not executable: {lz4_tool}')

    output.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [str(lz4_tool), '-dc', str(source)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        sys.stderr.buffer.write(result.stderr)
        raise SystemExit(result.returncode)

    count = extract_newc(result.stdout, output)

    if count != 654:
        raise SystemExit(
            f'unexpected stock vendor ramdisk entry count: {count}'
        )

    print(
        f'Extracted {count} stock vendor-ramdisk entries '
        f'into {output}'
    )


if __name__ == '__main__':
    main()
