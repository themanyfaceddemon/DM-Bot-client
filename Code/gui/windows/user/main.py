import dearpygui.dearpygui as dpg
from api import ChatClientModule
from systems.loc import Localization as loc


async def user_menu_setup():
    dpg.add_menu(
        label=loc.get_string("user_menu"),
        tag="user_menu_bar",
        parent="main_bar",
    )

    dpg.add_menu_item(
        label=loc.get_string("chat_window_lable"),
        parent="user_menu_bar",
        callback=ChatClientModule.create_window,
    )
