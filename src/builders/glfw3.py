from pathlib import Path

from . import common as cm
import os
import shlex


class GLFW3Builder(cm.Builder):
    def __init__(self, root_path: Path, deps: dict):
        super().__init__(root_path, deps, 'glfw3')

    def prepare(self) -> cm.Result:
        # ==============================================================================================
        # glfw3 must be built
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
        # Build glfw3 in target build directory
        # ==============================================================================================
        cwd: Path = self.target_build_dir
        os.chdir(str(cwd))

        # ==============================================================================================
        # Run cmake to generate build configurations
        # ==============================================================================================
        cmd = shlex.split(f'cmake ../../vendor/{self.name}')

        result = self.run_and_capture(self, cmd)
        if result.error != cm.Error.SUCCESS:
            return result

        # ==============================================================================================
        # Use 'msbuild' to build it
        # FIXME: msbuild not used on any platform except windows
        # ==============================================================================================
        cmd = ['msbuild', 'GLFW.sln', '/t:GLFW3\\glfw', '/clp:ErrorsOnly',
               '/p:Configuration=Release', '/p:Platform=x64']

        result = self.run_and_capture(self, cmd)
        if result.error != cm.Error.SUCCESS:
            return result

        # ==============================================================================================
        # Copy built library
        # ==============================================================================================
        lib_path: Path = self.target_build_dir / 'src' / 'Release'
        glfw_lib_path: Path = lib_path / 'glfw3.lib'

        result = self.copy_libs([glfw_lib_path])
        if result.error != cm.Error.SUCCESS:
            return result

        # ==============================================================================================
        # Clean-up, restore old cwd
        # and remove all other directories and files associated with the build
        # ==============================================================================================
        os.chdir(old_cwd)

        result = self.clean_build_dir([glfw_lib_path])
        if result.error != cm.Error.SUCCESS:
            return result

        return super().build()

    def clean(self) -> cm.Result:
        return super().clean()
