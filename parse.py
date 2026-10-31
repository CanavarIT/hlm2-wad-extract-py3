#!/usr/bin/env python3

# Copyright (c) 2015 Alex Yatskov <alex@foosoft.net>
# Author: Alex Yatskov <alex@foosoft.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Extract assets from Hotline Miami 2 WAD files."""

from __future__ import annotations

import argparse
import fnmatch
import struct
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Asset:
    filename: str
    offset: int
    length: int

    def extract(self, wad_data: bytes, data_start: int, extract_dir: Path) -> None:
        output_path = extract_dir / self.filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        start = data_start + self.offset
        end = start + self.length
        output_path.write_bytes(wad_data[start:end])


def extract(
    wad_file: Path,
    extract_dir: Path = Path("."),
    pattern: str = "*.*",
) -> None:
    print(f'Processing WAD file "{wad_file}"...')

    wad_data = wad_file.read_bytes()
    offset = 0

    (asset_count,) = struct.unpack_from("<I", wad_data, offset)
    offset += 4

    assets: list[Asset] = []
    for _ in range(asset_count):
        (name_len,) = struct.unpack_from("<I", wad_data, offset)
        offset += 4

        raw_name = struct.unpack_from(f"{name_len}s", wad_data, offset)[0]
        filename = raw_name.decode("utf-8", errors="replace")
        offset += name_len

        length, file_offset = struct.unpack_from("<2Q", wad_data, offset)
        offset += 16

        assets.append(Asset(filename, file_offset, length))

    matched = [a for a in assets if fnmatch.fnmatch(a.filename, pattern)]

    for i, asset in enumerate(matched, start=1):
        print(f'\t({i} / {len(matched)}) Extracting "{asset.filename}"...')
        asset.extract(wad_data, offset, extract_dir)

    print("Operation complete!")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract assets from Hotline Miami 2 WAD files"
    )
    parser.add_argument(
        "filenames",
        metavar="filename",
        nargs="+",
        type=Path,
        help="WAD files to extract",
    )
    parser.add_argument(
        "--pattern",
        default="*.*",
        help="asset file filter pattern (ex: *.ogg)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("."),
        help="output directory for asset files",
    )

    args = parser.parse_args()

    for filename in args.filenames:
        extract(filename, args.output, args.pattern)


if __name__ == "__main__":
    main()
