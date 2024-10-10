import dearpygui.dearpygui as dpg
from api import ChatClientModule
from systems.loc import Localization as loc


def settings_menu_setup():
    dpg.add_menu(
        label=loc.get_string("settings_menu"),
        tag="settings_menu_bar",
        parent="main_vp_bar",
    )

    dpg.add_menu_item(
        label=loc.get_string("toggle_viewport_fullscreen"),
        parent="settings_menu_bar",
        callback=lambda: dpg.toggle_viewport_fullscreen(),
    )

    dpg.add_menu_item(
        label=loc.get_string("popup_settigs_menu"),
        parent="settings_menu_bar",
        callback=ChatClientModule.create_window,
    )

    dpg.add_key_press_handler(parent="main_registry", callback=key_press_callback)


def key_press_callback(sender, app_data, user_data):
    if app_data == dpg.mvKey_F11:
        dpg.toggle_viewport_fullscreen()
