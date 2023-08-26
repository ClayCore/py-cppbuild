from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any
import os
import shutil
import subprocess as sp

from colorama import Fore


class Error(Enum):
    SUCCESS = 1
    IO_ERROR = auto()
    BUILD_TOOL_ERROR = auto()
    HEADER_NOT_FOUND = auto()
    LINKED_DEP_NOT_FOUND = auto()
    FILE_MISSING = auto()
    FILE_COPY_FAILED = auto()
    FILE_EXISTS_WARNING = auto()
    ARGUMENT_MISSING = auto()


@dataclass
class Result(object):
    error: Error = Error.SUCCESS
    result: Any = None


class Builder():

    @staticmethod
    def copytree(src, dst, ignore=None):
        # ==============================================================================================
        # Alternative to `shutil.copytree`
        # Overwrites files if they already exist (instead or throwing an exception)
        # ==============================================================================================
        if os.path.isdir(src):
            if not os.path.isdir(dst):
                os.makedirs(dst)
            files = os.listdir(src)
            if ignore is not None:
                ignored = ignore(src, files)
            else:
                ignored = set()
            for f in files:
                if f not in ignored:
                    Builder.copytree(os.path.join(src, f),
                                     os.path.join(dst, f), ignore)
        else:
            shutil.copyfile(src, dst)

    def copy_include(self) -> Result:
        # ==============================================================================================
        # Copies to source include directory
        # to the target include directory
        # ==============================================================================================
        include_dir = str(self.include_dir)
        tgt_include_dir = str(self.target_include_dir)

        if not self.target_include_dir.exists():
            self.target_include_dir.mkdir(parents=True)

        Builder.copytree(self.include_dir, self.target_include_dir)
        if not self.target_include_dir.exists():
            msg = f'{Fore.RED}[ERROR]: {Fore.RESET}' \
                f'failed to transact copy from \'{include_dir}\' to \'{tgt_include_dir}\''
            return Result(Error.FILE_COPY_FAILED, msg)

        return Result(Error.SUCCESS, None)

    def make_build_dir(self) -> Result:
        # ==============================================================================================
        # Creates source and target build directories
        # ==============================================================================================
        build_dir = str(self.build_dir)
        tgt_build_dir = str(self.target_build_dir)

        if not self.build_dir.exists():
            self.build_dir.mkdir(parents=True)

        if not self.build_dir.exists():
            msg = f'{Fore.RED}[ERROR]: {Fore.RESET}' \
                f'failed to create directory \'{build_dir}\''
            return Result(Error.FILE_MISSING, msg)

        if not self.target_build_dir.exists():
            self.target_build_dir.mkdir(parents=True)

        if not self.target_build_dir.exists():
            msg = f'{Fore.RED}[ERROR]: {Fore.RESET}' \
                f'failed to create directory \'{tgt_build_dir}\''
            return Result(Error.FILE_MISSING, msg)

        return Result(Error.SUCCESS, None)

    def run_and_capture(self, cmd: list[str]) -> Result:
        # ==============================================================================================
        # Runs a command and captures `stdout` and `stderr`
        # ==============================================================================================
        result: sp.CompletedProcess = sp.run(cmd)
        if result.returncode != 0:
            msg = f'{Fore.RED}[ERROR]: {Fore.RESET}' \
                'build command failed'
            msg += f'\nstdout: {result.stdout}'
            msg += f'\nstderr: {result.stderr}'
            return Result(Error.BUILD_TOOL_ERROR, msg)

        return Result(Error.SUCCESS, None)

    def copy_libs(self, libs: list[Path]) -> Result:
        # ==============================================================================================
        # Copy all libraries from `libs` to the target build directory
        # ==============================================================================================
        for lib in libs:
            if not lib.exists():
                msg = f'{Fore.RED}[ERROR]: {Fore.RESET}' \
                    'libraries failed to build'
                return Result(Error.FILE_MISSING, msg)

            shutil.copy2(lib, self.target_build_dir)

        return Result(Error.SUCCESS, None)

    def clean_build_dir(self, ignore: list[Path] = None) -> Result:
        # ==============================================================================================
        # Delete everything in the build directory *except*
        # for the files specified in the ignore list
        # ==============================================================================================
        if ignore == None:
            msg = f'{Fore.YELLOW}[WARNING]: {Fore.RESET}' \
                'no excluded files for clean'
            return Result(Error.ARGUMENT, msg)

        files = []
        for path in self.target_build_dir.glob('*'):
            for ignored in ignore:
                if str(path) != str(ignored):
                    files.append(str(path))

        for path in files:
            if os.path.isfile(path) and (not path.endswith(('.lib', '.a', '.so'))):
                _ = Path(path).unlink()
            if os.path.isdir(path):
                shutil.rmtree(path)

        return Result(Error.SUCCESS, None)

    def __init__(self, root_path: Path, deps: dict, name: str):
        self.root_path: Path = root_path
        self.deps: dict = deps
        self.name: str = name

        self.build_dir: Path = self.root_path / 'build' / self.name
        self.include_dir: Path = self.root_path / 'vendor' / self.name / 'include'

        self.target_build_dir: Path = self.root_path / 'deps' / self.name / 'bin'
        self.target_include_dir: Path = self.root_path / 'deps' / self.name / 'include'

    def prepare(self) -> Result:
        return Result(Error.SUCCESS, None)

    def build(self) -> Result:
        return Result(Error.SUCCESS, None)

    def clean(self) -> Result:
        return Result(Error.SUCCESS, None)
