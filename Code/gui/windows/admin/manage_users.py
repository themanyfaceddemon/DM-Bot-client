import logging

import dearpygui.dearpygui as dpg
import dpg_tools
from DMBotNetwork import Client
from systems.loc import Localization as loc


async def user_management(sender, app_data, user_data) -> None:
    if dpg.does_item_exist("user_management_window"):
        dpg.focus_item("user_management_window")
        return

    with dpg.window(
        label=loc.get_string("user_management_label"),
        tag="user_management_window",
        width=600,
        height=400,
        on_close=lambda: dpg.delete_item("user_management_window"),
    ):
        # Поле для поиска по пользователям
        dpg.add_input_text(
            tag="search_user_input",
            callback=filter_users,
            hint=loc.get_string("user_management_search_hint"),
        )
        await update_user_list()

        dpg_tools.center_window("user_management_window")


async def update_user_list(filter_term="") -> None:
    if dpg.does_item_exist("user_management_content"):
        dpg.delete_item("user_management_content")

    users: list = await Client.req_get_data("get_all_users", None)

    # Фильтрация пользователей по поисковому запросу
    filtered_users = [user for user in users if filter_term.lower() in user.lower()]

    with dpg.group(tag="user_management_content", parent="user_management_window"):
        with dpg.group(horizontal=True):
            with dpg.child_window(width=200, autosize_y=True):
                dpg.add_button(
                    label=loc.get_string("create_new_user_button"),
                    callback=open_create_user_window,
                )

                dpg.add_text(loc.get_string("user_management_user_logins"), wrap=0)
                for user in filtered_users:
                    dpg.add_button(
                        label=user,
                        callback=load_user_management_controls,
                        user_data=user,
                    )

            with dpg.child_window(
                width=300, tag="user_access_admin", autosize_y=True, autosize_x=True
            ):
                with dpg.group(tag="user_access_group"):
                    dpg.add_text(loc.get_string("user_not_loaded"), wrap=0)


async def load_user_management_controls(sender, app_data, user_data):
    if dpg.does_item_exist("user_controls"):
        dpg.delete_item("user_controls")

    with dpg.group(tag="user_controls", parent="user_access_admin"):
        dpg.add_button(
            label=loc.get_string("delete_user_button"),
            callback=confirm_delete_user,
            user_data=user_data,
        )

    await load_user_access(None, None, user_data)


async def confirm_delete_user(sender, app_data, user_data):
    if not dpg.is_key_down(dpg.mvKey_Shift):
        with dpg.window(
            label=loc.get_string("delete_confirmation_window"),
            modal=True,
            tag="delete_confirmation_window",
            width=300,
            height=150,
        ):
            dpg.add_text(loc.get_string("confirm_deletion_text"), wrap=0)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label=loc.get_string("yes"),
                    callback=delete_user,
                    user_data=user_data,
                )

                dpg.add_button(
                    label=loc.get_string("no"),
                    callback=lambda: dpg.delete_item("delete_confirmation_window"),
                )

                dpg_tools.center_window("delete_confirmation_window")
    else:
        await delete_user(None, None, user_data)


async def delete_user(sender, app_data, user_data):
    await Client.req_get_data("delete_user", None, login=user_data)
    dpg.delete_item("delete_confirmation_window")
    await update_user_list()


async def load_user_access(sender, app_data, user_data):
    if dpg.does_item_exist("user_access_group"):
        dpg.delete_item("user_access_group")

    user: dict[str, bool] = await Client.req_get_data(
        "get_access", None, login=user_data
    )

    if user is None:
        logging.error(f"User '{user_data}' not found.")
        return

    with dpg.group(tag="user_access_group", parent="user_access_admin"):
        if "full_access" in user:
            dpg.add_text(loc.get_string("full_access_warning_message"), wrap=0)
            return

        with dpg.child_window():
            for access_key, access_value in user.items():
                with dpg.group(horizontal=True):
                    uuid_text = dpg.generate_uuid()
                    dpg.add_text(
                        loc.get_string(f"text-{access_key}"), wrap=0, tag=uuid_text
                    )

                    dpg.add_checkbox(
                        default_value=access_value,
                        callback=toggle_user_access,
                        user_data=(user_data, access_key),
                    )

                    with dpg.tooltip(uuid_text):
                        dpg.add_text(loc.get_string(f"desc-{access_key}"), wrap=300)

                dpg.add_spacer(width=0, height=10)


async def toggle_user_access(sender, app_data, user_data):
    user_id = user_data[0]
    access_key = user_data[1]
    new_value = app_data

    changes = {access_key: new_value}

    await Client.req_net_func("change_access", login=user_id, changes=changes)


async def open_create_user_window(sender, app_data):
    if dpg.does_item_exist("create_user_window"):
        dpg.focus_item("create_user_window")
        return

    with dpg.window(
        label=loc.get_string("new_user_window_title"),
        tag="create_user_window",
        width=400,
        height=200,
        modal=True,
        on_close=lambda: dpg.delete_item("create_user_window"),
    ):
        dpg.add_text(loc.get_string("enter_new_user_login"), wrap=0)
        dpg.add_input_text(tag="new_user_login_input")

        dpg.add_text(loc.get_string("enter_new_user_password"), wrap=0)
        dpg.add_input_text(
            tag="new_user_password_input",
            password=True,
        )

        dpg.add_button(
            label=loc.get_string("create_new_user_button"),
            callback=create_user_button,
        )

        dpg_tools.center_window("create_user_window")


async def create_user_button(sender, app_data):
    new_login = dpg.get_value("new_user_login_input")
    new_password = dpg.get_value("new_user_password_input")

    if new_login and new_password:
        await create_new_user(None, None, [new_login, new_password])
        await update_user_list()


async def create_new_user(sender, app_data, user_data):
    await Client.req_get_data(
        "create_user", None, login=user_data[0], password=user_data[1]
    )


async def filter_users(sender, app_data):
    search_term = dpg.get_value("search_user_input")
    await update_user_list(filter_term=search_term)
