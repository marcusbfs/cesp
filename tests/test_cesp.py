import pytest
import os
from pathlib import Path
import shutil

import py7zr

import cesp

cesper = cesp.cesp()
cesper.setDots(True)
cesper.setSpecialChars(True)
cesper.setBrackets(True)
cesper.setUTF(True)
cesper.setNoChange(True)


CURRENT_DIR: Path = Path(__file__).parent.resolve()


def test_object_creation() -> None:
    assert cesper is not None
    assert type(cesper) == cesp.cesp


@pytest.fixture(scope="session", autouse=True)
def prepare_test_folder() -> None:  # type: ignore
    test_folder_7z = CURRENT_DIR / "test_folder.7z"
    test_folder: Path = test_folder_7z.with_name("test_folder")

    test_folder.mkdir(exist_ok=True)

    with py7zr.SevenZipFile(test_folder_7z, mode="r") as z:
        z.extractall(path=CURRENT_DIR)

    yield

    shutil.rmtree(test_folder, ignore_errors=True)


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("with space", "with_space"),
        ("coração.txt", "coracao.txt"),
        ("[brackets] (round) {weird} .mkv", "brackets_round_weird.mkv"),
        ("", ""),
        ("with.dots.mkv", "with_dots.mkv"),
    ],
)
def test_rename_function(test_input: str, expected: str) -> None:
    assert cesper._get_converted_name(test_input) == expected


def test_get_version() -> None:
    assert cesp.__version__ == cesper.getVersion()


def test_fetching_files_no_recursive() -> None:
    cesper.setPath(str(CURRENT_DIR / "test_folder"))
    cesper.setChange(cesp.ChangeItemMode.files)
    cesper.setRecursive(False)
    og, ren = cesper.fetch()
    assert len(og) == len(ren) == 1


def test_fetching_files_recursive() -> None:
    cesper.setPath(str(CURRENT_DIR / "test_folder"))
    cesper.setRecursive(True)
    cesper.setChange(cesp.ChangeItemMode.files)
    og, ren = cesper.fetch()
    assert len(og) == len(ren) == 5


def test_fetching_dirs_no_recursive() -> None:
    cesper.setPath(str(CURRENT_DIR / "test_folder"))
    cesper.setChange(cesp.ChangeItemMode.dirs)
    cesper.setRecursive(False)
    og, ren = cesper.fetch()
    assert len(og) == len(ren) == 2


def test_fetching_dirs_recursive() -> None:
    cesper.setPath(str(CURRENT_DIR / "test_folder"))
    cesper.setRecursive(True)
    cesper.setChange(cesp.ChangeItemMode.dirs)
    og, ren = cesper.fetch()
    assert len(og) == len(ren) == 2


def test_fetching_all_no_recursive() -> None:
    cesper.setPath(str(CURRENT_DIR / "test_folder"))
    cesper.setChange(cesp.ChangeItemMode.all)
    cesper.setRecursive(False)
    og, ren = cesper.fetch()
    assert len(og) == len(ren) == 3


def test_fetching_all_recursive() -> None:
    cesper.setPath(str(CURRENT_DIR / "test_folder"))
    cesper.setRecursive(True)
    cesper.setChange(cesp.ChangeItemMode.all)
    og, ren = cesper.fetch()
    assert len(og) == len(ren) == 7


@pytest.mark.parametrize("name, expected", [
    ('foo with spaces', 'foo_with_spaces'),
    ('foo ç with spaces', 'foo_ç_with_spaces'),
])
def test_remove_blank_spaces(name:str, expected:str) -> None:
    assert cesper._removeBlankSpaces(name) == expected
