import os
import shutil
from pathlib import Path

import py7zr
import pytest

import cesp

CURRENT_DIR: Path = Path(__file__).parent.resolve()


@pytest.fixture
def cesper() -> cesp.cesp:
    return cesp.cesp()


@pytest.fixture
def cesper_dubs() -> cesp.cesp:
    cesper = cesp.cesp()
    cesper.setDots(True)
    cesper.setUTF(True)
    cesper.setBrackets(True)
    cesper.setSpecialChars(True)
    cesper.setNoChange(True)
    return cesper


@pytest.fixture(scope="session", autouse=True)
def prepare_test_folder() -> None:  # type: ignore
    test_folder_7z = CURRENT_DIR / "test_folder.7z"
    test_folder: Path = test_folder_7z.with_name("test_folder")

    test_folder.mkdir(exist_ok=True)

    with py7zr.SevenZipFile(test_folder_7z, mode="r") as z:
        z.extractall(path=CURRENT_DIR)

    yield

    os.chdir(CURRENT_DIR)
    shutil.rmtree(test_folder, ignore_errors=True)
    if test_folder.is_dir():
        os.removedirs(test_folder)


def test_object_creation(cesper: cesp.cesp) -> None:
    assert cesper is not None
    assert type(cesper) == cesp.cesp


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("with space", "with_space"),
        ("coração.txt", "coracao.txt"),
        ("[brackets] (round) {weird} .mkv", "brackets_round_weird.mkv"),
        ("", ""),
        ("with.dots.mkv", "with_dots.mkv"),
        ("with^special&chars?.mkv", "withspecial_and_chars.mkv"),
    ],
)
def test_rename_function(
    test_input: str, expected: str, cesper_dubs: cesp.cesp
) -> None:
    assert cesper_dubs._get_converted_name(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("WITH SPACE", "WITH_SPACE"),
        ("CORAÇÃO.TXT", "CORACAO.TXT"),
        ("[BRACKETS] (ROUND) {WEIRD} .MKV", "BRACKETS_ROUND_WEIRD.MKV"),
        ("", ""),
        ("WITH.DOTS.MKV", "WITH_DOTS.MKV"),
        ("WITH^SPECIAL&CHARS?.MKV", "WITHSPECIAL_and_CHARS.MKV"),
    ],
)
def test_rename_all_uppercase_function(
    test_input: str, expected: str, cesper_dubs: cesp.cesp
) -> None:
    assert cesper_dubs._get_converted_name(test_input) == expected


def test_get_version(cesper: cesp.cesp) -> None:
    assert cesp.__version__ == cesper.getVersion()


def test_fetching_files_no_recursive(cesper_dubs: cesp.cesp) -> None:
    cesper_dubs.setPath(str(CURRENT_DIR / "test_folder"))
    cesper_dubs.setChange(cesp.ChangeItemMode.files)
    cesper_dubs.setRecursive(False)
    og, ren = cesper_dubs.fetch()
    assert len(og) == len(ren) == 1


def test_fetching_files_recursive(cesper_dubs: cesp.cesp) -> None:
    cesper_dubs.setPath(str(CURRENT_DIR / "test_folder"))
    cesper_dubs.setRecursive(True)
    cesper_dubs.setChange(cesp.ChangeItemMode.files)
    og, ren = cesper_dubs.fetch()
    assert len(og) == len(ren) == 5


def test_fetching_dirs_no_recursive(cesper_dubs: cesp.cesp) -> None:
    cesper_dubs.setPath(str(CURRENT_DIR / "test_folder"))
    cesper_dubs.setChange(cesp.ChangeItemMode.dirs)
    cesper_dubs.setRecursive(False)
    og, ren = cesper_dubs.fetch()
    assert len(og) == len(ren) == 2


def test_fetching_dirs_recursive(cesper_dubs: cesp.cesp) -> None:
    cesper_dubs.setPath(str(CURRENT_DIR / "test_folder"))
    cesper_dubs.setRecursive(True)
    cesper_dubs.setChange(cesp.ChangeItemMode.dirs)
    og, ren = cesper_dubs.fetch()
    assert len(og) == len(ren) == 2


def test_fetching_all_no_recursive(cesper_dubs: cesp.cesp) -> None:
    cesper_dubs.setPath(str(CURRENT_DIR / "test_folder"))
    cesper_dubs.setChange(cesp.ChangeItemMode.all)
    cesper_dubs.setRecursive(False)
    og, ren = cesper_dubs.fetch()
    assert len(og) == len(ren) == 3


def test_fetching_all_recursive(cesper_dubs: cesp.cesp) -> None:
    cesper_dubs.setPath(str(CURRENT_DIR / "test_folder"))
    cesper_dubs.setRecursive(True)
    cesper_dubs.setChange(cesp.ChangeItemMode.all)
    og, ren = cesper_dubs.fetch()
    assert len(og) == len(ren) == 7


@pytest.mark.parametrize(
    "name, expected",
    [
        ("foo with spaces", "foo_with_spaces"),
        ("foo ç with spaces", "foo_ç_with_spaces"),
    ],
)
def test_remove_blank_spaces(name: str, expected: str, cesper_dubs: cesp.cesp) -> None:
    assert cesper_dubs._removeBlankSpaces(name) == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("FOO WITH SPACES", "FOO_WITH_SPACES"),
        ("FOO Ç WITH SPACES", "FOO_Ç_WITH_SPACES"),
    ],
)
def test_remove_blank_spaces_upper(
    name: str, expected: str, cesper_dubs: cesp.cesp
) -> None:
    assert cesper_dubs._removeBlankSpaces(name) == expected


def test_actual_rename(cesper_dubs: cesp.cesp) -> None:
    test_folder = str(CURRENT_DIR / "test_folder")
    cesper_dubs.setPath(test_folder)
    cesper_dubs.setChange(cesp.ChangeItemMode.all)
    cesper_dubs.setNoChange(False)
    cesper_dubs.setRecursive(True)
    cesper_dubs.setIgnoredDirs([os.path.join(test_folder, "id")])

    og, ren = cesper_dubs.fetch()

    for f, new_f in zip(og, ren):
        cesper_dubs.rename_item(f, new_f)

    assert Path(Path(test_folder) / "utf" / "caoueuauad_nhau.txt").is_file()
    assert Path(Path(test_folder) / "special_chars" / "asd_adj.txt").is_file()
    assert Path(Path(test_folder) / "id" / "should be ignored.txt").is_file()
    assert Path(Path(test_folder) / "asd_asd_asd" / "file_with_spaces.txt").is_file()
