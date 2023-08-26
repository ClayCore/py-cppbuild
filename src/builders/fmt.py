from pathlib import Path

from . import common as cm
import os
import shlex


class FMTBuilder(cm.Builder):
    def __init__(self, root_path: Path, deps: dict):
        super().__init__(root_path, deps, 'fmt')

    def prepare(self) -> cm.Result:
        # ==============================================================================================
        # Strictly speaking, fmt does not need to be built
        # it's possible to use it as header-only library, but we build it
        # just for performance and size benefits
        # ==============================================================================================

        # ==============================================================================================
        # Create include directory and copy headers
        # ==============================================================================================
        result = self.copy_include()
        if result.error != cm.Error.SUCCESS:
            return result

        # ==============================================================================================
        # Create build directory
        # ==============================================================================================
        result = self.make_build_dir()
        if result.error != cm.Error.SUCCESS:
            return result

        return super().prepare()

    def build(self) -> cm.Result:
        # ==============================================================================================
        # Save current cwd
        # ==============================================================================================
        old_cwd: str = os.getcwd()

        # ==============================================================================================
        # Build fmt in target build directory
        # ==============================================================================================
        cwd: Path = self.build_dir
        os.chdir(str(cwd))

        # ==============================================================================================
        # Run cmake
        # ==============================================================================================
        cmd = shlex.split(f'cmake ../../vendor/{self.name}')

        result = self.run_and_capture(cmd)
        if result.error != cm.Error.SUCCESS:
            return result

        # ==============================================================================================
        # Use 'msbuild' to build it
        # FIXME: msbuild not used on any platform except windows
        # ==============================================================================================
        cmd = shlex.split(
            'msbuild FMT.sln /t:fmt /clp:ErrorsOnly /p:Configuration="Release" /p:Platform="x64"')

        result = self.run_and_capture(cmd)
        if result.error != cm.Error.SUCCESS:
            return result

        # ==============================================================================================
        # Copy built libraries
        # ==============================================================================================
        lib_path: Path = self.build_dir / 'Release' / 'fmt.lib'

        result = self.copy_libs([lib_path])
        if result.error != cm.Error.SUCCESS:
            return result

        # ==============================================================================================
        # Clean-up, restore old cwd
        # and remove all other directories and files associated with the build
        # ==============================================================================================
        os.chdir(old_cwd)

        result = self.clean_build_dir([lib_path])
        if result.error != cm.Error.SUCCESS:
            return result

        return super().build()

    def clean(self) -> cm.Result:
        return super().clean()
