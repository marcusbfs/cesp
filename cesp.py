# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import
import os
import time
import argparse
from enum import Enum, unique
from typing import List, Callable
import re
import logging

ListStr = List[str]

__author__ = "Marcus Bruno Fernandes Silva"
__version__ = "1.1.0"
__maintainer__ = "Marcus Bruno Fernandes Silva"
__email__ = "marcusbfs@gmail.com"

cesp_logger = logging.getLogger("cesp")
root_logger = logging.getLogger("main")


@unique
class changeItem(Enum):
    all = 1
    files = 2
    dirs = 3


class cesp:
    _special_chars = {
        u"?": "_",
        u"$": "_",
        u"%": "_",
        u"°": "o",
        u"!": "_",
        u"@": "_",
        u'"': "_",
        u"´": "",
        u"'": "",
        u"¨": "_",
        u"#": "_",
        u"|": "_",
        u"<": "_",
        u">": "_",
        u"/": "_",
        u"§": "_",
        u"\\": "_",
        u"&": "and",
        u"*": "_",
        u":": "_",
        u";": "_",
        u",": "_",
        u"+": "_",
        u"=": "_",
    }

    _utf_chars = {
        u"ç": "c",
        u"Ç": "C",
        u"~": "",
        u"^": "",
        u"ª": "a",
        u"ä": "a",
        u"ã": "a",
        u"â": "a",
        u"á": "a",
        u"à": "a",
        u"Ã": "A",
        u"Ä": "A",
        u"Â": "A",
        u"Á": "A",
        u"À": "A",
        u"é": "e",
        u"ê": "e",
        u"è": "e",
        u"É": "E",
        u"Ê": "E",
        u"È": "E",
        u"í": "i",
        u"î": "i",
        u"ì": "i",
        u"Í": "I",
        u"Î": "I",
        u"Ì": "I",
        u"º": "o",
        u"°": "o",
        u"ó": "o",
        u"ô": "o",
        u"ò": "o",
        u"õ": "o",
        u"Ó": "O",
        u"Ô": "O",
        u"Ò": "O",
        u"Õ": "O",
        u"ú": "u",
        u"ü": "u",
        u"û": "u",
        u"ù": "u",
        u"Ú": "U",
        u"Û": "U",
        u"Ù": "U",
        u"Ü": "U",
    }

    def __init__(self) -> None:
        self.logger = logging.getLogger("cesp")
        self.logger.debug("Constructing object")
        self._version = __version__
        self._path = os.path.realpath(os.getcwd())
        self._recursive = False
        self._ignored_dirs: ListStr = []
        self._ignored_exts: ListStr = []
        self._convert_utf = False
        self._convert_dots = False
        self._convert_brackets = False
        self._remove_special_chars = False
        self._quiet = False
        self._no_change = True
        self._change = changeItem.files

        self._print: Callable = lambda x: None
        self._update_print()

    # Commands

    def execute(self) -> int:
        self.logger.debug('"execute" called')
        original_files = []
        renamed_files = []

        if not os.path.isdir(self._path):
            raise ValueError("Invalid path.")

        original_path = os.getcwd()
        self.logger.debug('Original path "{}"'.format(original_path))
        self.logger.debug('Changing path to "{}"'.format(self._path))
        os.chdir(self._path)

        self.logger.debug("Walking directory tree and collecting names to be renamed")
        # Not recursive
        if not self._recursive:
            self.logger.debug("Non recursive mode")
            self.logger.debug("Change type is {}".format(self._change))
            if self._change == changeItem.files:
                original_files = [
                    f
                    for f in self._oslistdir(
                        ".",
                        ignoredDirs=self._ignored_dirs,
                        ignoredExts=self._ignored_exts,
                    )
                    if os.path.isfile(f)
                ]
            elif self._change == changeItem.dirs:
                original_files = [
                    f
                    for f in self._oslistdir(
                        ".",
                        ignoredDirs=self._ignored_dirs,
                        ignoredExts=self._ignored_exts,
                    )
                    if os.path.isdir(f)
                ]
            else:
                original_files = [
                    f
                    for f in self._oslistdir(
                        ".",
                        ignoredDirs=self._ignored_dirs,
                        ignoredExts=self._ignored_exts,
                    )
                ]
            renamed_files = [self._get_converted_name(f) for f in original_files]

        # Recursive
        else:
            self.logger.debug("Recursive mode")
            for root, dirs, files in os.walk(".", topdown=False):
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
                if self._change == changeItem.files:
                    wd = files
                elif self._change == changeItem.dirs:
                    wd = dirs
                else:
                    wd = files + dirs
                for f in wd:
                    new_f = self._get_converted_name(f)
                    original_files.append(os.path.join(root, f))
                    renamed_files.append(os.path.join(root, new_f))

        new_original_files = []
        new_renamed_files = []

        for f, new_f in zip(original_files, renamed_files):
            if f != new_f:
                new_original_files.append(f)
                new_renamed_files.append(new_f)

        original_files = new_original_files
        renamed_files = new_renamed_files

        self.logger.debug("Collected {} files to be renamed".format(len(renamed_files)))

        for f, new_f in zip(original_files, renamed_files):
            if f != new_f:
                if os.path.exists(new_f):
                    self._print(new_f + " already exists")
                else:
                    self._print(f + " -> " + new_f)
                    if not self._no_change:
                        os.rename(f, new_f)

        self.logger.debug('Returning to "{}"'.format(original_path))
        os.chdir(original_path)
        self.logger.debug("execute method finished")
        return 0

    # helper Functions

    def _oslistdir(
        self, path: str, ignoredDirs: ListStr = [], ignoredExts: ListStr = []
    ) -> ListStr:
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
            self._print = lambda *args, **kwargs: print(*args, **kwargs)

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

    def setIgnoredDirs(self, ignoredDirs: ListStr) -> None:
        self._ignored_dirs = ignoredDirs
        self._fullPathIgnoredDirs()

    def setIgnoredExts(self, ignoredExts: ListStr) -> None:
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

    def setChange(self, changeOption: changeItem) -> None:
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

    def getIgnoredDirs(self) -> ListStr:
        return self._ignored_dirs

    def getIgnoredExtensions(self) -> ListStr:
        return self._ignored_exts

    def whatToChange(self) -> changeItem:
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
        "files": changeItem.files,
        "dirs": changeItem.dirs,
        "all": changeItem.all,
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

    logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=args.loglevel, format=logging_format)

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

    root_logger.debug("Calling cesper.execute()")
    cesper.execute()

    root_logger.debug(
        "Finished program in {:.3f} seconds".format(time.time() - start_time)
    )


if __name__ == "__main__":
    main()
