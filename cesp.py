# -*- coding: utf-8 -*-

from __future__ import absolute_import, annotations, division, print_function

import argparse
import logging
import os
import re
import time
from enum import Enum, unique
from typing import Any, Callable, List, Tuple

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress

listStr = List[str]
RENAME_DELAY = 0.1

__author__ = "Marcus Bruno Fernandes Silva"
__maintainer__ = __author__
__email__ = "marcusbfs@gmail.com"
__version__ = "1.4.0"

console = Console()

cesp_logger = logging.getLogger("cesp")
root_logger = logging.getLogger("main")


@unique
class ChangeItemMode(Enum):
    all = 1
    files = 2
    dirs = 3


class cesp:
    _special_chars = {
        "?": "_",
        "$": "_",
        "%": "_",
        "°": "o",
        "!": "_",
        "@": "_",
        '"': "_",
        "´": "",
        "'": "",
        "¨": "_",
        "#": "_",
        "|": "_",
        "<": "_",
        ">": "_",
        "/": "_",
        "§": "_",
        "\\": "_",
        "&": "and",
        "*": "_",
        ":": "_",
        ";": "_",
        ",": "_",
        "+": "_",
        "=": "_",
    }

    _utf_chars = {
        "ç": "c",
        "Ç": "C",
        "~": "",
        "^": "",
        "ª": "a",
        "ä": "a",
        "ã": "a",
        "â": "a",
        "á": "a",
        "à": "a",
        "Ã": "A",
        "Ä": "A",
        "Â": "A",
        "Á": "A",
        "À": "A",
        "é": "e",
        "ê": "e",
        "è": "e",
        "É": "E",
        "Ê": "E",
        "È": "E",
        "í": "i",
        "î": "i",
        "ì": "i",
        "Í": "I",
        "Î": "I",
        "Ì": "I",
        "º": "o",
        "°": "o",
        "ó": "o",
        "ô": "o",
        "ò": "o",
        "õ": "o",
        "Ó": "O",
        "Ô": "O",
        "Ò": "O",
        "Õ": "O",
        "ú": "u",
        "ü": "u",
        "û": "u",
        "ù": "u",
        "Ú": "U",
        "Û": "U",
        "Ù": "U",
        "Ü": "U",
    }

    def __init__(self) -> None:
        self.logger = logging.getLogger("cesp")
        self.logger.debug("Constructing object")
        self._path = os.path.realpath(os.getcwd())
        self._recursive = False
        self._ignored_dirs: listStr = []
        self._ignored_exts: listStr = []
        self._convert_utf = False
        self._convert_dots = False
        self._convert_brackets = False
        self._remove_special_chars = False
        self._quiet = False
        self._no_change = True
        self._change: ChangeItemMode = ChangeItemMode.files

        self._print: Callable[[Any], None] = lambda x: None
        self._update_print()
        self.original_path = os.getcwd()

    # Commands

    def fetch(self) -> Tuple[listStr, listStr]:
        self.logger.debug('"fetch" called')
        original_files = []
        renamed_files = []

        if not os.path.isdir(self._path):
            raise ValueError("Invalid path.")

        self.logger.debug('Original path "{}"'.format(self.original_path))
        self.logger.debug('Changing path to "{}"'.format(self._path))
        os.chdir(self._path)

        self.logger.debug("Walking directory tree and collecting names to be renamed")
        for root, dirs, files in os.walk(".", topdown=True):
            files = [
                f
                for f in files
                if not f.startswith(".") and self._isPathGood(os.path.join(root, f))
            ]
            dirs = [
                d
                for d in dirs
                if not d.startswith(".") and self._isPathGood(os.path.join(root, d))
            ]
            if self._change == ChangeItemMode.files:
                wd = files
            elif self._change == ChangeItemMode.dirs:
                wd = dirs
            else:
                wd = files + dirs
            for f in wd:
                new_f = self._get_converted_name(f)
                if f != new_f:
                    original_files.append(os.path.join(root, f))
                    renamed_files.append(os.path.join(root, new_f))

            if not self._recursive:
                break

        self.logger.debug("Collected {} files to be renamed".format(len(renamed_files)))

        return list(reversed(original_files)), list(reversed(renamed_files))

    def return_to_original_path(self) -> None:
        self.logger.debug('Returning to path "{}"'.format(self.original_path))
        os.chdir(self.original_path)

    def rename_item(self, f: str, new_f: str) -> None:
        if os.path.exists(new_f):
            self._print(f"[bold]{new_f}[/] already exists")
        else:
            base_new_f = os.path.basename(new_f)
            sep = r"\\"
            fmt_new_f = f"{os.path.dirname(new_f)}{sep}[bold]{base_new_f}[/]"
            self._print(f"[dim]{f}[/] -> {fmt_new_f}")
            if not self._no_change:
                os.rename(f, new_f)

    def rename_list(self, original_files: listStr, renamed_files: listStr) -> int:

        self.logger.debug("Renaming files")
        for f, new_f in zip(original_files, renamed_files):
            self.rename_item(f, new_f)

        self.logger.debug("Renamed {} files".format(len(renamed_files)))
        self.logger.debug("rename_list method finished")
        return 0

    # helper Functions

    def _oslistdir(
        self, path: str, ignoredDirs: listStr = [], ignoredExts: listStr = []
    ) -> listStr:
        self.logger.debug("_oslistdir called")
        list_dirs = []
        ignoredDirs = [f[:-1] if f[-1] == "/" else f for f in ignoredDirs]
        ignoredExts = ["." + f for f in ignoredExts if not f.startswith(".")]
        list_dirs = [
            f
            for f in os.listdir(path)
            if (self._isPathGood(f) and not f.startswith("."))
        ]
        return list_dirs

    def _isPathGood(self, path: str) -> bool:
        return self._isDirGood(path) and self._isExtensionGood(path)

    def _isDirGood(self, dir: str) -> bool:
        full_dir = os.path.realpath(dir)
        for ignored_dir in self._ignored_dirs:
            if ignored_dir in full_dir:
                return False
        return True

    def _isExtensionGood(self, file: str) -> bool:
        ext = os.path.splitext(file)[-1]
        return ext not in self._ignored_exts

    def _update_print(self) -> None:
        self.logger.debug("_update_print called")
        if self._quiet:
            self._print = lambda *args, **kwargs: None
        else:
            self._print = lambda *args, **kwargs: console.print(*args, **kwargs)

    def _get_converted_name(self, name: str) -> str:
        if self._convert_utf:
            name = self._convertUTF(name)
        if self._convert_dots:
            name = self._convertDots(name)
        if self._convert_brackets:
            name = self._convertBrackets(name)
        if self._remove_special_chars:
            name = self._removeSpecialChars(name)

        name = self._removeBlankSpaces(name)
        return name

    def _removeBlankSpaces(self, name: str) -> str:
        name = re.sub(r"\s+", r"_", name)
        name = re.sub(r"_+", r"_", name)
        name = re.sub(r"(^_|_$)", r"", name)
        name = re.sub(r"_\.", r".", name)
        return name

    def _removeSpecialChars(self, name: str) -> str:
        for char in name:
            if char in self._special_chars:
                name = name.replace(char, self._special_chars[char])
        return name

    def _convertUTF(self, name: str) -> str:
        for char in name:
            if char in self._utf_chars:
                name = name.replace(char, self._utf_chars[char])
        return name

    def _convertDots(self, name: str) -> str:
        base_name = os.path.splitext(name)[0]
        name_extension = os.path.splitext(name)[-1]
        name = base_name.replace(".", "_").replace(",", "_") + name_extension
        return name

    def _convertBrackets(self, name: str) -> str:
        return re.sub(r"\(|\)|\[|\]|\{|\}", r"", name)

    def _fixDotInIgnoredExtensions(self) -> None:
        for i in range(len(self._ignored_exts)):
            ext = self._ignored_exts[i]
            if not ext.startswith("."):
                self._ignored_exts[i] = "." + ext

    def _fullPathIgnoredDirs(self) -> None:
        for i in range(len(self._ignored_dirs)):
            self._ignored_dirs[i] = os.path.realpath(
                os.path.join(self._path, self._ignored_dirs[i])
            )

    # Setters

    def setRecursive(self, recursive: bool) -> None:
        self._recursive = recursive

    def setIgnoredDirs(self, ignoredDirs: listStr) -> None:
        self._ignored_dirs = ignoredDirs
        self._fullPathIgnoredDirs()

    def setIgnoredExts(self, ignoredExts: listStr) -> None:
        self._ignored_exts = ignoredExts
        self._fixDotInIgnoredExtensions()

    def setUTF(self, convertUTF: bool) -> None:
        self._convert_utf = convertUTF

    def setDots(self, convertDots: bool) -> None:
        self._convert_dots = convertDots

    def setBrackets(self, convertBrackets: bool) -> None:
        self._convert_brackets = convertBrackets

    def setSpecialChars(self, removeSpecialChars: bool) -> None:
        self._remove_special_chars = removeSpecialChars

    def setQuiet(self, quiet: bool) -> None:
        self._quiet = quiet
        self._update_print()

    def setNoChange(self, noChange: bool) -> None:
        self._no_change = noChange

    def setChange(self, changeOption: ChangeItemMode) -> None:
        self._change = changeOption

    def setPath(self, path: str) -> None:
        self._path = os.path.realpath(path)

    # Getters

    @staticmethod
    def getVersion() -> str:
        return __version__

    def getPath(self) -> str:
        return self._path

    def isRecursive(self) -> bool:
        return self._recursive

    def getIgnoredDirs(self) -> listStr:
        return self._ignored_dirs

    def getIgnoredExtensions(self) -> listStr:
        return self._ignored_exts

    def whatToChange(self) -> ChangeItemMode:
        return self._change

    def isNoChange(self) -> bool:
        return self._no_change


def main() -> None:

    start_time = time.time()

    version_message = (
        "cesp "
        + cesp.getVersion()
        + os.linesep
        + os.linesep
        + "Author: "
        + __maintainer__
        + os.linesep
        + "email: "
        + __email__
    )

    desc = (
        version_message
        + os.linesep
        + os.linesep
        + "Converts blank space to underscore and other characters to avoid problems"
    )

    list_of_choices = {
        "files": ChangeItemMode.files,
        "dirs": ChangeItemMode.dirs,
        "all": ChangeItemMode.all,
    }
    choices_keys = list(list_of_choices.keys())

    parser = argparse.ArgumentParser(
        description=desc, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("path", nargs="?", default=os.getcwd(), help="path")

    parser.add_argument(
        "-c",
        "--change",
        dest="change",
        nargs=1,
        default=[choices_keys[0]],
        help="rename files, directories or all",
        choices=choices_keys,
    )

    parser.add_argument(
        "-r", dest="recursive", help="recursive action", action="store_true"
    )

    parser.add_argument(
        "-d", "--dots", dest="dots", help="replace dots", action="store_true"
    )

    parser.add_argument(
        "-u", "--UTF", dest="UTF", help="subs. UTF-8 chars", action="store_true"
    )

    parser.add_argument(
        "-b", dest="brackets", help="remove brackets", action="store_true"
    )

    parser.add_argument(
        "-s",
        "--special-chars",
        dest="special_chars",
        help="remove special characters",
        action="store_true",
    )

    parser.add_argument(
        "-i",
        "--ignore-dirs",
        dest="ignoredirs",
        default=[],
        help="ignore dirs",
        nargs="+",
    )

    parser.add_argument(
        "-I",
        "--ignore-exts",
        dest="ignoreexts",
        default=[],
        help="ignore exts",
        nargs="+",
    )

    parser.add_argument(
        "-q", "--quiet", dest="quiet", help="no verbosity", action="store_true"
    )

    parser.add_argument(
        "-n",
        "--no-change",
        dest="nochange",
        help="do not make actual changes",
        action="store_true",
    )

    parser.add_argument(
        "--debug",
        help="display debug level information",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )

    parser.add_argument("-v", "--version", action="version", version=version_message)

    args = parser.parse_args()

    FORMAT = "%(message)s"
    logging.basicConfig(
        level=args.loglevel,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler(console=console)],
    )

    root_logger.debug("Args passed: {}".format(args))

    cesper: cesp = cesp()
    root_logger.debug("Passings args to cesper object")
    cesper.setRecursive(args.recursive)
    cesper.setIgnoredDirs(args.ignoredirs)
    cesper.setIgnoredExts(args.ignoreexts)
    cesper.setUTF(args.UTF)
    cesper.setDots(args.dots)
    cesper.setBrackets(args.brackets)
    cesper.setQuiet(args.quiet)
    cesper.setNoChange(args.nochange)
    cesper.setChange(list_of_choices[args.change[0]])
    cesper.setSpecialChars(args.special_chars)
    cesper.setPath(args.path)

    root_logger.debug("Calling cesper.fetch()")

    og_files: listStr = []
    ren_files: listStr = []

    fetching_message = "Fetching files..."
    with console.status(
        fetching_message,
    ) as status:
        og_files, ren_files = cesper.fetch()

    files_num = len(og_files)

    console.print(f"[bold green]OK![/] {fetching_message}")
    console.print(f"Found {files_num} files")

    if args.nochange:
        cesper.rename_list(og_files, ren_files)
        console.print("[bold red]No changes were made[/]")
    else:
        with Progress(console=console) as progress:
            task = progress.add_task(description="Renaming...", total=files_num)
            for f, new_f in zip(og_files, ren_files):
                cesper.rename_item(f, new_f)
                time.sleep(RENAME_DELAY)
                progress.advance(task, 1)

    cesper.return_to_original_path()

    elapsed_time = time.time() - start_time

    console.print(f"Finished in {elapsed_time:.2f} seconds")

    root_logger.debug("Finished program in {:.2f} seconds".format(elapsed_time))


if __name__ == "__main__":
    main()
