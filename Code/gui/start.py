from pathlib import Path

import dearpygui.dearpygui as dpg
from dearpygui_async import DearPyGuiAsync
from DMBotNetwork import Client
from misc import decode_string
from root_path import ROOT_PATH
from systems.loc import Localization as loc
from .fonts_setup import FontManager


class DMClientApp:
    def __init__(self):
        self.dpg_async = DearPyGuiAsync()

    def setup(self):
        dpg.create_context()
        FontManager.load_fonts()
        dpg.create_viewport(title=loc.get_string("main-app-name"), width=600, min_width=600, height=400, min_height=400)
        dpg.setup_dearpygui()
        self._create_warning_window()

    def _create_warning_window(self):
        with dpg.window(label="Warning", tag="warning_window", no_move=True, no_close=True, no_collapse=True, width=380, no_resize=True):
            dpg.add_text(loc.get_string("main_text_warning_window"), wrap=380)
            dpg.add_button(label=loc.get_string("yes_warning_window"), callback=self._on_yes)
            dpg.add_button(label=loc.get_string("no_warning_window"), callback=self._on_no)

    def _on_yes(self, *args):
        dpg.delete_item("warning_window")
        self._create_connect_window()

    def _on_no(self, *args):
        self.stop()

    def _create_connect_window(self):
        if dpg.does_item_exist("connect_window"):
            dpg.focus_item("connect_window")
            return
        
        with dpg.window(label="Connect", tag="connect_window", no_close=True, no_collapse=True, no_move=True, width=380):
            dpg.add_text(loc.get_string("connect_main_text"))
            
            dpg.add_input_text(hint=loc.get_string("connect_login_hint")   , tag="connect_login")
            dpg.add_input_text(hint=loc.get_string("connect_password_hint"), tag="connect_password", password=True)
            dpg.add_input_text(hint=loc.get_string("connect_host_hint")    , tag="connect_host")
            dpg.add_input_int (label=loc.get_string("connect_port_lable")  , tag="connect_port")
            dpg.add_button(label=loc.get_string("connect_button"), callback=self._run_client)
            
    async def _run_client(self, *args):
        await Client.close_connection()
        
        login_value = decode_string(dpg.get_value("connect_login"))
        password_value = decode_string(dpg.get_value("connect_password"))
        host_value = decode_string(dpg.get_value("connect_host"))
        port_value = dpg.get_value("connect_port")

        Client.set_login(login_value)
        Client.set_password(password_value)
        Client.set_host(host_value)
        Client.set_port(port_value)

        server_path = Path(ROOT_PATH) / "Content" / "Servers"
        Client.set_server_file_path(server_path)
        
        await Client.connect()
        
        if Client._listen_task is None: # FIXME: Так делать нельзя, но проверить законектились ли мы иначе на текущий момент невозможно. Cain. DM-Bot-net v 0.0.12
            with dpg.window(no_title_bar=True, modal=True, width=380) as con_err:
                dpg.add_text(loc.get_string("on_connect_error_msg"), wrap=380)
                
                dpg.add_button(label=loc.get_string("ok"), callback=lambda: dpg.delete_item(con_err))
        
        else:
            dpg.delete_item("connect_window")
            # TODO: Запрос других окон с сервера.
            
    def run(self):
        dpg.show_viewport()
        self.dpg_async.run()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def stop(self):
        dpg.stop_dearpygui()
