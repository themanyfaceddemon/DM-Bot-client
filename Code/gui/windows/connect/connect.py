import asyncio
import logging
import shutil
import time
import zipfile
from pathlib import Path

import dearpygui.dearpygui as dpg
import dpg_tools
from DMBotNetwork import Client
from gui.windows.admin import admin_menu_setup
from gui.windows.user import user_menu_setup
from systems.discord_rpc import DiscordRPC
from systems.file_work import AppPath
from systems.loc import Localization as loc


async def connect(login, password, host, port, use_registration):
    if Client.is_connected():
        return

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
            use_registration=use_registration,
            content_path=AppPath.get_servers_path(),
        )
        await Client.connect(host, port)
        await asyncio.wait_for(_connected(), 15)

    except TimeoutError:
        msg = loc.get_string("timeout_error")
        _err_window(msg)
        return

    except ValueError:
        msg = loc.get_string("null_values_set")
        _err_window(msg)
        return

    except Exception as err:
        msg = loc.get_string("error_msg", err=str(err))
        _err_window(msg)
        return

    await DiscordRPC.update(
        f'Connect to "{Client.get_server_name()}" as "{login}"',
        start=int(time.time()),
    )

    dpg.set_item_label(
        "login_in_vp_bar", loc.get_string("cur_login", login=Client.get_login())
    )

    AppPath.update_cur_server_name()

    dpg.delete_item("connect_window")

    await _load_server_content()
    await _load_vp_menu_obj()


async def _load_server_content() -> None:
    await _download_content_from_server()
    loc.load_translations(Path(AppPath.get_cur_server_path() / "loc" / "rus"))


async def _load_vp_menu_obj() -> None:
    access = await Client.req_get_data(
        "get_access", None, login=Client.get_login()
    )  # TODO: Добавить access в Client для более удобного доступа

    if "full_access" in access:
        admin_menu_setup()

    user_menu_setup()


async def _download_content_from_server() -> None:
    server_content_path: Path = AppPath.get_cur_server_path()
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


def _err_window(msg):
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
