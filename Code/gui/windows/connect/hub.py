import dearpygui.dearpygui as dpg
import aiohttp
import dpg_tools
from .direct_connect import create_direct_connect_window
import webbrowser

url = "http://194.87.94.191:8000/servers/all/"


async def create_hub_window():
    with dpg.window(
        tag="hub_window",
        label="Server Hub",
        width=800,
        height=600,
        no_resize=True,
        no_move=True,
        no_collapse=True,
    ):
        with dpg.menu_bar():
            with dpg.menu(label="Действия"):
                dpg.add_menu_item(label="Обновить список", callback=refresh_server_list)
                dpg.add_menu_item(label="Прямое подключение", callback=dr_connect)

            with dpg.menu(label="Поиск"):
                dpg.add_input_text(
                    label="Поиск", tag="search_input", callback=filter_servers
                )

        with dpg.group(horizontal=True):
            with dpg.child_window(width=200, height=0, border=True, tag="server_list"):
                dpg.add_text("Список серверов")

                with dpg.group(tag="servers_group"):
                    servers = await get_servers()
                    for server in servers:
                        dpg.add_button(
                            label=server["name"],
                            callback=show_server_description,
                            user_data=server,
                        )

            with dpg.child_window(
                width=-1, height=0, border=True, tag="server_description"
            ):
                dpg.add_text("Описание сервера")
                dpg.add_text(
                    "Нажмите на сервер слева, чтобы увидеть описание.",
                )

    dpg_tools.center_window("hub_window")


def show_server_description(sender, app_data, user_data):
    dpg.delete_item("server_description", children_only=True)

    # Стиль для заголовков
    title_color = [0, 150, 255]  # Синий для заголовков

    with dpg.group(horizontal=True, parent="server_description"):
        dpg.add_text("Название:", color=title_color)
        dpg.add_text(user_data["name"].strip())

    dpg.add_spacer(height=10, parent="server_description")

    dpg.add_text("Описание:", color=title_color, parent="server_description")
    dpg.add_text(user_data["desc"].strip(), wrap=0, parent="server_description")

    dpg.add_spacer(height=10, parent="server_description")

    dpg.add_text("Теги:", color=title_color, parent="server_description")
    if user_data["tags"]:
        with dpg.group(parent="server_description"):
            for tag in user_data["tags"]:
                dpg.add_text(f"• {tag.strip()}", bullet=True)
    else:
        dpg.add_text("Нет тегов", color=[100, 100, 100], parent="server_description")

    dpg.add_spacer(height=10, parent="server_description")

    dpg.add_text(
        "Дополнительные ссылки:", color=title_color, parent="server_description"
    )
    if user_data["additional_links"]:
        with dpg.group(parent="server_description"):
            for type, link in user_data["additional_links"].items():
                dpg.add_text(f"{type.strip()}: ", color=title_color)
                dpg.add_text(
                    link.strip(),
                    color=[0, 0, 255],
                    callback=lambda s, a, l=link: webbrowser.open(l),
                )
    else:
        dpg.add_text("Нет ссылок", color=[100, 100, 100], parent="server_description")

    dpg.add_spacer(height=10, parent="server_description")
    
    dpg.add_button(
        label="Подключиться",
        parent="server_description",
        callback=connect_server_hub,
        user_data=[user_data["ip"], user_data["port"]],
    )


async def connect_server_hub(sender, app_data, user_data):
    print(user_data) # TODO: Доделать


async def dr_connect(sender, app_data, user_data):
    dpg.delete_item("hub_window")
    await create_direct_connect_window()


async def get_servers():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()

            else:
                return []


async def refresh_server_list(sender, app_data, user_data):
    await _update_server_list(await get_servers())


async def filter_servers(sender, app_data, user_data):
    search_query = dpg_tools.decode_string((dpg.get_value("search_input"))).lower()
    filtered_servers = [
        server
        for server in await get_servers()
        if search_query in server["name"].lower()
    ]
    await _update_server_list(filtered_servers)


async def _update_server_list(servers):
    dpg.delete_item("servers_group", children_only=True)
    for server in servers:
        dpg.add_button(
            label=server["name"],
            callback=show_server_description,
            user_data=server,
            parent="servers_group",
        )
