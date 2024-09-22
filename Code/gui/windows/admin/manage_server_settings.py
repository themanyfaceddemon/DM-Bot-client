import dearpygui.dearpygui as dpg
import dpg_tools
from DMBotNetwork import Client
from systems.loc import Localization as loc


async def manage_server_settings(sender, app_data, user_data) -> None:
    if dpg.does_item_exist("manage_server_settings_window"):
        dpg.focus_item("manage_server_settings_window")
        return

    with dpg.window(
        label=loc.get_string("manage_server_settings_lable"),
        tag="manage_server_settings_window",
        width=400,
        height=200,
        on_close=lambda: dpg.delete_item("manage_server_settings_window"),
    ):
        cur_server_settings: dict = await Client.req_get_data(
            "get_server_settings", None
        )
        with dpg.child_window(autosize_x=True, autosize_y=True):
            with dpg.group(horizontal=True):
                dpg.add_text(loc.get_string("allow_registration_text"), wrap=0)
                dpg.add_checkbox(
                    default_value=cur_server_settings.get("allow_registration", False),
                    callback=_change_server_settings,
                    user_data="allow_registration",
                )
            dpg.add_spacer(width=0, height=10)

            dpg.add_text(loc.get_string("max_players_text"), wrap=0)
            dpg.add_input_int(
                min_value=-1,
                min_clamped=True,
                max_value=100,
                max_clamped=True,
                default_value=cur_server_settings.get("max_players", 0),
                callback=_change_server_settings,
                user_data="max_players",
            )
            dpg.add_spacer(width=0, height=10)

            dpg.add_text(loc.get_string("timeout_text"), wrap=0)
            dpg.add_input_double(
                min_value=1.0,
                min_clamped=True,
                max_value=60.0,
                max_clamped=True,
                default_value=cur_server_settings.get("timeout", 1),
                callback=_change_server_settings,
                user_data="timeout",
            )

            dpg_tools.center_window("manage_server_settings_window")


async def _change_server_settings(sender, app_data, user_data) -> None:
    await Client.req_net_func("change_server_settings", type=user_data, value=app_data)
