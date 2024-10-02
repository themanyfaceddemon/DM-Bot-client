import dearpygui.dearpygui as dpg
import dpg_tools
from systems.loc import Localization as loc

from .connect import connect


async def create_direct_connect_window():
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
        dpg.add_text(loc.get_string("direct_connect_main_text"))
        dpg.add_input_text(
            hint=loc.get_string("connect_login_hint"), tag="connect_login"
        )

        dpg.add_input_text(
            hint=loc.get_string("connect_password_hint"),
            tag="connect_password",
            password=True,
        )

        dpg.add_input_text(hint=loc.get_string("connect_host_hint"), tag="connect_host")

        dpg.add_input_int(
            label=loc.get_string("connect_port_lable"),
            tag="connect_port",
            min_clamped=True,
            min_value=0,
        )

        dpg.add_button(
            label=loc.get_string("login_button"),
            callback=_connect_to_server,
            user_data=False,
        )

        dpg.add_button(
            label=loc.get_string("register_button"),
            callback=_connect_to_server,
            user_data=True,
        )

        dpg_tools.center_window("connect_window")


async def _connect_to_server(sender, app_data, user_data) -> None:
    if dpg.is_key_down(dpg.mvKey_Control):  # For debug
        dpg.set_value("connect_login", "owner")
        dpg.set_value("connect_password", "owner_password")
        dpg.set_value("connect_host", "localhost")
        dpg.set_value("connect_port", 5000)

    login = dpg_tools.decode_string(dpg.get_value("connect_login"))
    password = dpg_tools.decode_string(dpg.get_value("connect_password"))
    host = dpg_tools.decode_string(dpg.get_value("connect_host"))
    port = dpg.get_value("connect_port")

    await connect(
        login=login,
        password=password,
        port=port,
        host=host,
        use_registration=user_data,
    )
