import dearpygui.dearpygui as dpg
import asyncio
import requests
import dpg_tools

url = "http://194.87.94.191:5000/hub"

# Функция для получения данных с сервера
async def fetch_server_data():
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP ошибка: {http_err}")
        return []
    except Exception as err:
        print(f"Другая ошибка: {err}")
        return []

# Колбек для присоединения к серверу
def connect_to_server(sender, app_data, user_data):
    server_info = user_data
    print(f"Присоединение к серверу: {server_info['name']} ({server_info['ip_address']}:{server_info['port']})")

# Колбек для обновления списка серверов
async def update_hub_window():
    servers = await fetch_server_data()
    
    if dpg.does_item_exist("servers_group"):
        dpg.delete_item("servers_group")

    if servers:
        with dpg.group(tag="servers_group", parent="hub_window"):
            dpg.add_text("Список доступных серверов:")
            for server in servers:
                with dpg.group(horizontal=True):
                    with dpg.collapsing_header(label=server['name'], default_open=False):
                        dpg.add_text(f"Описание: {server['description']}")
                        dpg.add_text(f"IP: {server['ip_address']}")
                        dpg.add_text(f"Порт: {server['port']}")
                        dpg.add_text(f"Теги: {', '.join(server['tags'])}")
                        if server['additional_links']:
                            dpg.add_text("Дополнительные ссылки:")
                            for link_name, link_url in server['additional_links'].items():
                                dpg.add_text(f"{link_name}: {link_url}")
                    
                    dpg.add_button(label="Присоединиться", callback=connect_to_server, user_data=server)
    else:
        with dpg.group(tag="servers_group", parent="hub_window"):
            dpg.add_text("Серверов нет или произошла ошибка при получении данных.")

# Колбек для кнопки "Обновить"
def refresh_servers_callback(sender, app_data):
    asyncio.create_task(update_hub_window())

# Функция для создания окна хаба
async def create_hub_window():
    if dpg.does_item_exist("hub_window"):
        dpg.focus_item("hub_window")
    else:
        with dpg.window(label="Список серверов", tag="hub_window"):
            dpg.add_button(label="Обновить", callback=refresh_servers_callback)
            dpg.add_group(tag="servers_group")  # Группа для списка серверов

        await update_hub_window()
