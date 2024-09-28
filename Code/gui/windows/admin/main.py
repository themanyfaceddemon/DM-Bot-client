import dearpygui.dearpygui as dpg
from systems.loc import Localization as loc

from .manage_server_settings import manage_server_settings
from .manage_users import user_management


async def admin_menu_setup():
    dpg.add_menu(
        label=loc.get_string("admin_control_menu"),
        tag="admin_control_menu_bar",
        parent="main_bar",
    )

    dpg.add_menu_item(
        label=loc.get_string("user_management_label"),
        parent="admin_control_menu_bar",
        callback=user_management,
    )

    dpg.add_menu_item(
        label=loc.get_string("manage_server_settings_lable"),
        parent="admin_control_menu_bar",
        callback=manage_server_settings,
    )
