import asyncio
import sys

from systems.network import ClientUnit


def menu_address() -> int:
    """Выводит следующее меню:
    1. Ввести адрес
    2. Завершить программу

    Returns:
        int: Номер выбранного пункта
    """
    print("\n1. Ввести адрес")
    print("2. Завершить программу\n")
    try:
        choice = int(input("Введите действие: "))
        if choice not in (1, 2):
            print("Выбрано неверное действие!")
            return menu_address()
        
    except ValueError:
        print("Некорректный ввод. Введите число.")
        return  menu_address()
    
    return choice

def menu_auth() -> int:
    """Выводит следующее меню:
    1. Зарегистрироваться
    2. Авторизоваться

    Returns:
        int: Номер выбранного пункта
    """
    print("\n1. Зарегистрироваться")
    print("2. Авторизоваться")
    print("3. Выйти\n")
    try:
        choice = int(input("Введите действие: "))
        if choice not in range(1, 4):
            print("Выбрано неверное действие!")
            return menu_auth()
        
    except ValueError:
        print("Некорректный ввод. Введите число.")
        return  menu_auth()
    
    return choice

def dm_menu() -> int:
    """Выводит следующее меню:
    1. Выйти с системы
    2. Сменить пароль
    3. Сменить доступ пользователя
    4. Удалить пользователя
    5. Скачать контент с сервера
    6. Подключиться через WebSocket
    7. Отправить данные через WebSocket
    8. Отключиться от WebSocket

    Returns:
        int: Номер выбранного пункта
    """
    print("\n1. Выйти с системы")
    print("2. Сменить пароль")
    print("3. Сменить доступ пользователя")
    print("4. Удалить пользователя")
    print("5. Скачать контент с сервера")
    print("6. Подключиться через WebSocket")
    print("7. Отправить данные через WebSocket")
    print("8. Отключиться от WebSocket\n")
    try:
        choice = int(input("Введите действие: "))
        if choice not in range(1, 9):
            print("Выбрано неверное действие!")
            return dm_menu()
        
    except ValueError:
        print("Некорректный ввод. Введите число.")
        return  dm_menu()
    
    return choice


def display_title_screen() -> None:
    """Выводит логотип на экран
    """
    from art import tprint
    tprint("DM bot client")
    print('')


def user_input_ip(client_unit: ClientUnit) -> bool:
    """Ввод IP пользователем

    Returns:
        bool: True если ip валиден
    """
    try:
        user_ip: str = input("Введите IP сервера: ")
        
        # Cain - Защита от дурака. 
        # 127,0/0,1^5000 будет преобразовано в 127.0.0.1:5000

        # nixsilvam404 - А если там вообще точек не поставят?
        
        # Cain - Ну бля. Скилл ишью.
        user_ip = user_ip.translate(str.maketrans({
            ',': '.', 
            '/': '.', 
            '^': ':'
        }))
        if client_unit.check_ip(user_ip):
            print("IP-адрес успешно проверен.")
            return True
        
    except ConnectionError as err:
        print(f"Ошибка при подключении к {user_ip}. Ошибка: {err}")
    
    return False


def user_input_registration(client_unit: ClientUnit) -> bool:
    """Регистрация пользователя. Пользователь задает данные логина и пароля. 
    Пароль вводится повторно и проверяется.

    Returns:
        bool: True если регистрация прошла успешно
    """
    try:
        user_login_reg: str = input("Введите логин: ")

        while True:
            user_password_reg: str = input("Введите пароль: ")
            user_password_reg_2: str = input("Повторите пароль: ")
            if user_password_reg == user_password_reg_2:
                break
            
            print("Пароли не совпадают. Пожалуйста, попробуйте еще раз.")
        
        client_unit.register(user_login_reg, user_password_reg)
        print("Регистрация выполнена успешно.")
        return True
    
    except ConnectionError as err:
        print(f"Возникла проблема при подключении к сети. Проверьте своё соединение. Подробная ошибка: {err}")
    
    except Exception as err:
        print(f"Произошла ошибка при регистрации: {err}")
    
    return False
    

def user_input_login(client_unit: ClientUnit) -> bool:
    """Логин в аккаунт пользователя. Вводит логин и пароль. 

    Returns:
        bool: True если логин выполнен успешно
    """
    try:
        user_login: str = input("Введите логин: ")
        user_password: str = input("Введите пароль: ")
        client_unit.login(user_login, user_password)
        print("Логин выполнен успешно.")
        return True
    
    except ConnectionError as err:
        print(f"Возникла проблема при подключении к сети. Проверьте своё соединение. Подробная ошибка: {err}")
    
    except Exception as err:
        print(f"Произошла ошибка при попытке логина: {err}")
    
    return False
    

def user_input_change_password(client_unit: ClientUnit) -> None:
    """Меняет пароль пользователя
    """
    try:
        user_new_password: str = input("Введите новый пароль: ")
        client_unit.change_password(user_new_password)
        print("Пароль успешно изменён.")

    except ConnectionError as err:
        print(f"Возникла проблема при подключении к сети. Проверьте своё соединение. Подробная ошибка: {err}")


def user_input_change_access(client_unit: ClientUnit) -> None:
    """Меняет доступ пользователя
    """
    try:
        user_login: str = input("Введите логин пользователя: ")
        access_rights = input("Введите новые права доступа в формате 'key1:True,key2:False': ")
        new_access = {k: v == 'True' for k, v in (item.split(':') for item in access_rights.split(','))}
        client_unit.change_access(user_login, new_access)
        print("Права доступа успешно изменены.")

    except ConnectionError as err:
        print(f"Возникла проблема при подключении к сети. Проверьте своё соединение. Подробная ошибка: {err}")


def user_input_delete_user(client_unit: ClientUnit) -> None:
    """Удаляет пользователя
    """
    try:
        user_login: str = input("Введите логин пользователя: ")
        client_unit.delete_user(user_login)
        print("Пользователь успешно удален.")

    except ConnectionError as err:
        print(f"Возникла проблема при подключении к сети. Проверьте своё соединение. Подробная ошибка: {err}")


def user_input_download_content(client_unit: ClientUnit) -> None:
    """Скачивает контент с сервера
    """
    try:
        client_unit.download_server_content()
        print("Контент успешно скачан.")

    except ConnectionError as err:
        print(f"Возникла проблема при подключении к сети. Проверьте своё соединение. Подробная ошибка: {err}")


async def user_input_connect_ws(client_unit: ClientUnit) -> None:
    """Подключается к WebSocket
    """
    try:
        await client_unit.connect()
        print("WebSocket подключен.")

    except ConnectionError as err:
        print(f"Возникла проблема при подключении к сети. Проверьте своё соединение. Подробная ошибка: {err}")


async def user_input_send_ws_data(client_unit: ClientUnit) -> None:
    """Отправляет данные через WebSocket
    """
    try:
        data = input("Введите данные в формате 'key1:value1,key2:value2': ")
        data_dict = {k: v for k, v in (item.split(':') for item in data.split(','))}
        await client_unit.send_data(data_dict)
        print("Данные успешно отправлены через WebSocket.")

    except ConnectionError as err:
        print(f"Возникла проблема при подключении к сети. Проверьте своё соединение. Подробная ошибка: {err}")


async def user_input_disconnect_ws(client_unit: ClientUnit) -> None:
    """Отключается от WebSocket
    """
    try:
        await client_unit.disconnect()
        print("WebSocket отключен.")

    except ConnectionError as err:
        print(f"Возникла проблема при подключении к сети. Проверьте своё соединение. Подробная ошибка: {err}")


def main() -> None:
    client_unit = ClientUnit()
    display_title_screen()
    menu_status: int = 1
    
    while True:
        if menu_status == 1:
            user_input = menu_address()
            match user_input:
                case 1:
                    if user_input_ip(client_unit):
                        menu_status = 2
                    continue
                
                case 2:
                    sys.exit(0)
        
        if menu_status == 2:
            user_input = menu_auth()
            match user_input:
                case 1:
                    if user_input_registration(client_unit):
                        menu_status = 3
                    continue
                
                case 2:
                    if user_input_login(client_unit):
                        menu_status = 3
                    continue
                
                case 3:
                    sys.exit(0)
        
        if menu_status == 3:
            user_input = dm_menu()
            match user_input:
                case 1:
                    sys.exit(0)
                
                case 2:
                    user_input_change_password(client_unit)
                    continue
                
                case 3:
                    user_input_change_access(client_unit)
                    continue
                
                case 4:
                    user_input_delete_user(client_unit)
                    continue
                
                case 5:
                    user_input_download_content(client_unit)
                    continue
                
                case 6:
                    asyncio.run(user_input_connect_ws(client_unit))
                    continue
                
                case 7:
                    asyncio.run(user_input_send_ws_data(client_unit))
                    continue
                
                case 8:
                    asyncio.run(user_input_disconnect_ws(client_unit))
                    continue

            
if __name__ == '__main__':
    main()
