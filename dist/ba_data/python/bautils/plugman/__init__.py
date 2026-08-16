# Released under the MIT License. See LICENSE for details.
#
"""All Server plugins are defined in this directory."""

# ba_meta require api 9

import os
import importlib

from typing import override

import bascenev1 as bs
from bautils.tools import package_loading_context


# ba_meta export babase.Plugin
class RegisterPlugins(bs.Plugin):
    """Register all plugins in this module."""

    @override
    def on_app_running(self) -> None:
        with package_loading_context(name="Plugin System"):
            self._auto_import_all_modules()

    def _auto_import_all_modules(self) -> None:

        current_dir = os.path.dirname(__file__)
        package = __name__  # 'plugins'

        try:
            for filename in os.listdir(current_dir):
                if filename.endswith(".py") and filename != "__init__.py":
                    module_name = filename[:-3]
                    full_module = f"{package}.{module_name}"
                    importlib.import_module(full_module)
        except Exception as e:
            print(f"ERROR in RegisterPlugins: Failed to import module: {e}")
            pass
