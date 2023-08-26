from pathlib import Path

from . import common as cm


class SPDLOGBuilder(cm.Builder):
    def __init__(self, root_path: Path, deps: dict):
        super().__init__(root_path, deps, 'spdlog')

    def prepare(self) -> cm.Result:
        # ==============================================================================================
        # spdlog is a header only library, no need to build anything
        # ==============================================================================================

        # ==============================================================================================
        # Create include directory and copy headers
        # ==============================================================================================
        result = self.copy_include()
        if result.error != cm.Error.SUCCESS:
            return result

        return super().prepare()

    def build(self) -> cm.Result:
        return super().build()

    def clean(self) -> cm.Result:
        return super().clean()
