from pathlib import Path

from . import common as cm
import os
import shlex


class BGFXBuilder(cm.Builder):
    def __init__(self, root_path: Path, deps: dict):
        super().__init__(root_path, deps, 'bgfx')

    def prepare(self) -> cm.Result:
        # ==============================================================================================
        # bgfx, bimg, and bx dont utilize build directories (but we need them anyways)
        # and have to be built together in one project
        # ==============================================================================================
        result = self.copy_include()
        if result.error != cm.Error.SUCCESS:
            return result

        result = self.make_build_dir()
        if result.error != cm.Error.SUCCESS:
            return result

        return super().prepare()

    def build(self) -> cm.Result:
        # ==============================================================================================
        # Ensure linked dependencies (bimg, bx) also exist
        # ==============================================================================================
        bimg_exists = self.deps['bimg'].exists()
        bx_exists = self.deps['bx'].exists()

        if (not bimg_exists) or (not bx_exists):
            msg = '[BGFX]: bimg and bx must be present for build'
            return cm.Result(cm.Error.LINKED_DEP_NOT_FOUND, msg)

        # ==============================================================================================
        # Save current cwd
        # ==============================================================================================
        old_cwd: str = os.getcwd()

        # ==============================================================================================
        # Change cwd to build bgfx
        # ==============================================================================================
        cwd: Path = self.deps[self.name].include_dir.parent
        os.chdir(str(cwd))

        # ==============================================================================================
        # Run genie
        # TODO: change platform and genie generation based on OS
        # ==============================================================================================
        cmd = shlex.split('../bx/tools/bin/windows/genie vs2019')
        result = self.run_and_capture(cmd)
        if result.error != cm.Error.SUCCESS:
            return result

        # ==============================================================================================
        # Use 'msbuild' to build everything
        # FIXME: msbuild not used on any platform besides windows
        # ==============================================================================================
        cmd = shlex.split(
            'msbuild .build/projects/vs2019/bgfx.sln /clp:ErrorsOnly /p:Configuration="Release" /p:Platform="x64"')
        result = self.run_and_capture(cmd)
        if result.error != cm.Error.SUCCESS:
            return result

        # ==============================================================================================
        # Copy built libraries
        # FIXME: path depends on os and platform
        # ==============================================================================================
        lib_path: Path = self.deps[self.name].include_dir.parent / \
            '.build' / 'win64_vs2019' / 'bin'
        bgfx_lib_path: Path = lib_path / 'bgfxRelease.lib'
        bimg_lib_path: Path = lib_path / 'bimgRelease.lib'
        bx_lib_path: Path = lib_path / 'bxRelease.lib'
        lib_paths = [bgfx_lib_path, bimg_lib_path, bx_lib_path]

        result = self.copy_libs(lib_paths)
        if result.error != cm.Error.SUCCESS:
            return result

        # ==============================================================================================
        # Clean-up, restore old cwd
        # ==============================================================================================
        os.chdir(old_cwd)

        result = self.clean_build_dir(lib_paths)
        if result.error != cm.Error.SUCCESS:
            return result

        return super().build()

    def clean(self) -> cm.Result:
        return super().clean()
