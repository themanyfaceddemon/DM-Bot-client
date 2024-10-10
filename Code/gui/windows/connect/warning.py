import dearpygui.dearpygui as dpg
import dpg_tools
from systems.discord_rpc import DiscordRPC
from systems.loc import Localization as loc

from .hub import create_hub_window


def create_warning_window():
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
        dpg.add_button(label=loc.get_string("yes_warning_window"), callback=_on_yes)
        dpg.add_button(label=loc.get_string("no_warning_window"), callback=_on_no)
        dpg_tools.center_window("warning_window")


async def _on_yes(*args):
    dpg.delete_item("warning_window")

    await DiscordRPC.connect()
    await DiscordRPC.update("Connect to server...")

    await create_hub_window()


def _on_no(*args):
    from gui.dm_client_app import DMClientApp

    DMClientApp.stop()
