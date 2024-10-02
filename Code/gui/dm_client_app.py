import dearpygui.dearpygui as dpg
from dearpygui_async import DearPyGuiAsync
from gui.windows.settings import settings_menu_setup
from systems.loc import Localization as loc

from .fonts_setup import FontManager
from .windows.connect import create_warning_window
from DMBotNetwork import Client


class DMClientApp:
    _dpg_async = DearPyGuiAsync()

    def __init__(self):
        dpg.create_context()
        FontManager.load_fonts()

        dpg.create_viewport(
            title=loc.get_string("main-app-name"),
            width=600,
            min_width=600,
            height=400,
            min_height=400,
        )

        dpg.setup_dearpygui()
        dpg.show_viewport()

        dpg.add_handler_registry(tag="main_registry")
        dpg.add_viewport_menu_bar(tag="main_vp_bar")

        dpg.add_menu_item(
            label=loc.get_string("cur_login", login="NC"),
            tag="login_in_vp_bar",
            parent="main_vp_bar",
            enabled=False,
        )

        Client.set_callback_on_disconect(DMClientApp.on_disconect)

        settings_menu_setup()

        create_warning_window()

    @classmethod
    def on_disconect(cls, reason) -> None:
        with dpg.window(no_title_bar=True):
            dpg.add_text(loc.get_string("on_dissconect_error", reason=reason))

            dpg.add_button(label=loc.get_string("ok"), callback=lambda: cls.stop())

    @classmethod
    def run(cls) -> None:
        cls._dpg_async.run()
        dpg.start_dearpygui()
        dpg.destroy_context()

    @classmethod
    def stop(cls) -> None:
        dpg.stop_dearpygui()
