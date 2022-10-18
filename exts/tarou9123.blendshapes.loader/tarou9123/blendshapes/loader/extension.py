__all__ = ["BlendShapesLoaderExtension"]

from .usd_operation import Usd_Operation
from .window import MainWindow
from functools import partial
import asyncio
import omni.ext
import omni.kit.ui
import omni.ui as ui


class BlendShapesLoaderExtension(omni.ext.IExt):
    """The entry point for Example Window"""

    WINDOW_NAME = "BlendShapes Loader"
    MENU_PATH = f"Window/{WINDOW_NAME}"

    def on_startup(self):
        ui.Workspace.set_show_window_fn(BlendShapesLoaderExtension.WINDOW_NAME, partial(self.show_window, None))

        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item(
                BlendShapesLoaderExtension.MENU_PATH, self.show_window, toggle=True, value=True
            )
        ui.Workspace.show_window(BlendShapesLoaderExtension.WINDOW_NAME)

    def on_shutdown(self):
        self._menu = None
        if self._window is not None:
            self._window.destroy()
            self._window = None
        # Deregister the function that shows the window from omni.ui
        ui.Workspace.set_show_window_fn(BlendShapesLoaderExtension.WINDOW_NAME, None)
        self._u_operation.destroy()
        editor_menu = omni.kit.ui.get_editor_menu()
        editor_menu.remove_item(BlendShapesLoaderExtension.MENU_PATH)

    def _set_menu(self, value):
        """Set the menu to create this window on and off"""
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            editor_menu.set_value(BlendShapesLoaderExtension.MENU_PATH, value)

    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._window:
            self._window.destroy()
            self._window = None
            self._u_operation.destroy()

    def _visiblity_changed_fn(self, visible):
        # Called when the user pressed "X"
        self._set_menu(visible)
        if not visible:
            # Destroy the window, since we are creating new window
            # in show_window
            asyncio.ensure_future(self._destroy_window_async())

    def show_window(self, menu, value):
        if value:
            self._window = MainWindow(BlendShapesLoaderExtension.WINDOW_NAME, width=600, height=500)
            self._window.set_visibility_changed_fn(self._visiblity_changed_fn)
            self._u_operation = Usd_Operation(self._window)
        elif self._window:
            self._window.visible = False
