from pathlib import Path

from . import common as cm
import os
import shlex


class SFMLBuilder(cm.Builder):
    def __init__(self, root_path: Path, deps: dict):
        super().__init__(root_path, deps, 'sfml')

    def prepare(self) -> cm.Result:
        # ==============================================================================================
        # sfml must be built
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
        # Build SFML in target build directory
        # ==============================================================================================
        cwd: Path = self.build_dir
        os.chdir(str(cwd))

        # ==============================================================================================
        # Run cmake to generate build configurations
        # ==============================================================================================
        cmd = shlex.split(
            f'cmake ../../../vendor/{self.name} -DCMAKE_BUILD_TYPE=Release')

        result = self.run_and_capture(cmd)
        if result.error != cm.Error.SUCCESS:
            return result

        # ==============================================================================================
        # Use 'msbuild' to build it
        # FIXME: msbuild not used on any platform except windows
        # ==============================================================================================
        cmd = ['msbuild', 'SFML.sln', '/clp:ErrorsOnly',
               '/t:CMake\\ALL_BUILD', '/p:Configuration=Release', '/p:Platform=x64']

        result = self.run_and_capture(cmd)
        if result.error != cm.Error.SUCCESS:
            return result

        # ==============================================================================================
        # Copy built library
        # ==============================================================================================
        lib_path: Path = self.build_dir / 'lib' / 'Release'
        sfml_audio_lib: Path = lib_path / 'sfml-audio.lib'
        sfml_graphics_lib: Path = lib_path / 'sfml-graphics.lib'
        sfml_main_lib: Path = lib_path / 'sfml-main.lib'
        sfml_network_lib: Path = lib_path / 'sfml-network.lib'
        sfml_system_lib: Path = lib_path / 'sfml-system.lib'
        sfml_window_lib: Path = lib_path / 'sfml-window.lib'

        lib_paths = [sfml_audio_lib, sfml_graphics_lib, sfml_main_lib,
                     sfml_network_lib, sfml_system_lib, sfml_window_lib]

        result = self.copy_libs(lib_paths)
        if result.error != cm.Error.SUCCESS:
            return result

        # ==============================================================================================
        # Clean-up, restore old cwd
        # and remove all other directories and files associated with the build
        # ==============================================================================================
        os.chdir(old_cwd)

        result = self.copy_libs(lib_paths)
        if result.error != cm.Error.SUCCESS:
            return result

        return super().build()

    def clean(self) -> cm.Result:
        return super().clean()
