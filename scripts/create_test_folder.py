import os
from pathlib import Path

import py7zr

CURRENT_DIR: Path = Path(__file__).parent.resolve()

test_folder_7z = CURRENT_DIR.parent / "test_folder.7z"
test_folder: Path = test_folder_7z.with_name("test_folder")

test_folder.mkdir(exist_ok=True)


with py7zr.SevenZipFile(test_folder_7z, mode="r") as z:
    z.extractall(path=CURRENT_DIR.parent)
