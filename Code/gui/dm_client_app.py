import asyncio
import logging
import shutil
import time
import zipfile
from pathlib import Path

import dearpygui.dearpygui as dpg
import dpg_tools
from dearpygui_async import DearPyGuiAsync
from DMBotNetwork import Client
from root_path import ROOT_PATH
from systems.discord_rpc import DiscordRPC
from systems.loc import Localization as loc

from .fonts_setup import FontManager
from .windows.admin import admin_main_window


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

        DMClientApp._create_warning_window()

    @classmethod
    def _create_warning_window(cls):
        with dpg.window(
            label="Warning",
            tag="warning_window",
            no_move=True,
            no_close=True,
            no_collapse=True,
            width=380,
            height=150,
            no_resize=True,
        ):
            dpg.add_text(loc.get_string("main_text_warning_window"), wrap=0)
            dpg.add_button(
                label=loc.get_string("yes_warning_window"), callback=cls._on_yes
            )
            dpg.add_button(
                label=loc.get_string("no_warning_window"), callback=lambda: cls._on_no()
            )

            dpg_tools.center_window("warning_window")

    @classmethod
    async def _on_yes(cls, *args):
        dpg.delete_item("warning_window")
        await DMClientApp._create_connect_window()

    @classmethod
    def _on_no(cls, *args):
        cls.stop()

    @classmethod
    async def _create_connect_window(cls):
        """Создание окна подключения"""
        await DiscordRPC.connect()
        await DiscordRPC.update("Connect to server...")

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
            height=380,
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
                label=loc.get_string("connect_port_lable"),
                tag="connect_port",
                min_clamped=True,
                min_value=0,
            )

            dpg.add_button(
                label=loc.get_string("login_button"),
                callback=DMClientApp._connect_to_server,
                user_data=False,
            )
            dpg.add_button(
                label=loc.get_string("register_button"),
                callback=DMClientApp._connect_to_server,
                user_data=True,
            )

            dpg_tools.center_window("connect_window")

    @classmethod
    async def _connect_to_server(cls, sender, app_data, user_data):
        if Client.is_connected():
            return

        if not user_data and dpg.is_key_down(dpg.mvKey_Control):  # For debug
            login = "owner"
            password = "owner_password"
            host = "localhost"
            port = 5000

        else:
            login = dpg_tools.decode_string(dpg.get_value("connect_login"))
            password = dpg_tools.decode_string(dpg.get_value("connect_password"))
            host = dpg_tools.decode_string(dpg.get_value("connect_host"))
            port = dpg.get_value("connect_port")

        async def _connected():
            while True:
                if not Client.is_connected():
                    await asyncio.sleep(0.5)
                    continue

                break

        try:
            Client.setup(
                login=login,
                password=password,
                use_registration=user_data,
                content_path=Path(ROOT_PATH / "Content" / "Servers"),
            )

            await Client.connect(host, port)
            await asyncio.wait_for(_connected(), 15)

        except TimeoutError:
            msg = loc.get_string("timeout_error")
            cls._err_window(msg)
            return

        except ValueError:
            msg = loc.get_string("null_values_set")
            cls._err_window(msg)
            return

        except Exception as err:
            msg = loc.get_string("error_msg", err=str(err))
            cls._err_window(msg)
            return

        await DiscordRPC.update(
            f'Connect to "{Client.get_server_name()}" as "{login}"',
            start=int(time.time()),
        )

        dpg.delete_item("connect_window")

        await cls.setup_start_windows()

    @classmethod
    def _err_window(cls, msg):
        with dpg.window(
            label="Error",
            tag="error_connect_window",
            no_collapse=True,
            modal=True,
            width=400,
            height=200,
        ) as err_window:
            dpg.add_text(msg, wrap=0)
            dpg.add_button(
                label=loc.get_string("ok"), callback=lambda: dpg.delete_item(err_window)
            )

            dpg_tools.center_window(err_window)

    @classmethod
    async def setup_start_windows(cls) -> None:
        await cls.download_content_from_server()
        loc.load_translations(
            Path(
                ROOT_PATH
                / "Content"
                / "Servers"
                / Client.get_server_name()
                / "loc"
                / "rus"
            )
        )
        access = await Client.req_get_data("get_access", None, login=Client.get_login())
        dpg.add_viewport_menu_bar(tag="main_bar")

        dpg.add_menu_item(
            label=loc.get_string("cur_login", login=Client.get_login()),
            parent="main_bar",
            enabled=False,
        )

        # При всём желании, проверка прав проходит на сервере. Даже не пытайтесь.
        if "full_access" in access:
            await admin_main_window()

    @classmethod
    async def download_content_from_server(cls) -> None:
        server_content_path: Path = (
            Path(ROOT_PATH) / "Content" / "Servers" / Client.get_server_name()
        )
        local_hash_path = server_content_path / "content_hash"

        if local_hash_path.exists():
            with local_hash_path.open("r") as file:
                local_hash = file.read().strip()
        else:
            local_hash = None

        server_hash = await Client.req_get_data("get_server_content_hash", None)

        if local_hash == server_hash:
            return

        else:
            if server_content_path.exists():
                for item in server_content_path.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)

        answer = await Client.req_get_data("download_server_content", None)
        if answer != "done":
            logging.error(f"Error while download content: {answer}")
            return

        file_path = server_content_path / "server_content.zip"
        extract_path = server_content_path

        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        file_path.unlink()

        with local_hash_path.open("w") as file:
            file.write(server_hash)

    @classmethod
    def run(cls):
        cls._dpg_async.run()
        dpg.start_dearpygui()
        dpg.destroy_context()

    @classmethod
    def stop(cls):
        dpg.stop_dearpygui()
