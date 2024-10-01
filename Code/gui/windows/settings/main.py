import dearpygui.dearpygui as dpg
from api import ChatClientModule
from systems.loc import Localization as loc


async def settings_menu_setup():
    dpg.add_menu(
        label=loc.get_string("settings_menu"),
        tag="settings_menu_bar",
        parent="main_bar",
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
