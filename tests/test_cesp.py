import pytest

import cesp

cesper = cesp.cesp()
cesper.setDots(True)
cesper.setSpecialChars(True)
cesper.setBrackets(True)
cesper.setUTF(True)


def test_object_creation() -> None:
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
    ],
)
def test_rename_function(test_input: str, expected: str) -> None:
    assert cesper._get_converted_name(test_input) == expected


def test_get_version() -> None:
    assert cesp.__version__ == cesper.getVersion()
