import atexit

import dearpygui.dearpygui as dpg
from dearpygui_async import DearPyGuiAsync
from pypresence import Presence
from systems.loc import Localization as loc

from .fonts_setup import FontManager


class DMClientApp:
    _dpg_async = DearPyGuiAsync()
    rpc = Presence(1227926138400276561)
    
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

        DMClientApp.rpc.connect()
        DMClientApp.rpc.update(state="Nya~")

        atexit.register(self.rpc.close)

        self._create_warning_window()

    @classmethod
    def _create_warning_window(cls):
        with dpg.window(
            label="Warning",
            tag="warning_window",
            no_move=True,
            no_close=True,
            no_collapse=True,
            width=380,
            no_resize=True,
        ):
            dpg.add_text(loc.get_string("main_text_warning_window"), wrap=380)
            dpg.add_button(
                label=loc.get_string("yes_warning_window"), callback=cls._on_yes
            )
            dpg.add_button(
                label=loc.get_string("no_warning_window"), callback=cls._on_no
            )

    @classmethod
    def _on_yes(cls, *args):
        dpg.delete_item("warning_window")
        cls._create_connect_window()

    @classmethod
    def _on_no(cls, *args):
        cls.stop()

    @classmethod
    def _create_connect_window(cls):
        if dpg.does_item_exist("connect_window"):
            dpg.focus_item("connect_window")
            return

        with dpg.window(
            label="Connect",
            tag="connect_window",
            no_close=True,
            no_collapse=True,
            no_move=True,
            width=380,
        ):
            dpg.add_text(loc.get_string("connect_main_text"))

            dpg.add_input_text(
                hint=loc.get_string("connect_login_hint"), tag="connect_login"
            )
            dpg.add_input_text(
                hint=loc.get_string("connect_password_hint"),
                tag="connect_password",
                password=True,
            )
            dpg.add_input_text(
                hint=loc.get_string("connect_host_hint"), tag="connect_host"
            )
            dpg.add_input_int(
                label=loc.get_string("connect_port_lable"), tag="connect_port"
            )
            dpg.add_button(
                label=loc.get_string("connect_button")
            )

    @classmethod
    def run(cls):
        dpg.show_viewport()
        cls._dpg_async.run()
        dpg.start_dearpygui()
        dpg.destroy_context()

    @classmethod
    def stop(cls):
        dpg.stop_dearpygui()
