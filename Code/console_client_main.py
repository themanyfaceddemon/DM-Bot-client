import sys

from main_impt import server_system


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

    Returns:
        int: Номер выбранного пункта
    """
    print("\n1. Выйти с системы")
    print("2. Сменить пароль\n")
    try:
        choice = int(input("Введите действие: "))
        if choice not in (1, 2):
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


def user_input_ip() -> bool:
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
        
        server_system.setup_server_ip(user_ip)
        # TODO: Сохранение IP сервера
        
        return True
        
    except ConnectionError as err:
        print(f"Ошибка при подключении к {user_ip}. Ошибка: {err}")
    
    return False


def user_input_registration() -> bool:
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
            else:
                print("Пароли не совпадают. Пожалуйста, попробуйте еще раз.")

        server_system.register(user_login_reg, user_password_reg)
        print("Регистрация выполнена успешно.")
        return True
    
    except ConnectionError as err:
        print(f"Возникла проблема при подключении к сети. Проверьте своё соединение. Подробная ошибка: {err}")
    except Exception as err:
        print(f"Произошла ошибка при регистрации: {err}")
    
    return False
    

def user_input_login() -> bool:
    """Логин в аккаунт пользователя. Вводит логин и пароль. 

    Returns:
        bool: True если логин выполнен успешно
    """
    try:
        user_login: str = input("Введите логин: ")
        user_password: str = input("Введите пароль: ")
        server_system.login(user_login, user_password)
        print("Логин выполнен успешно.")
        return True
    
    except ConnectionError as err:
        print(f"Возникла проблема при подключении к сети. Проверьте своё соединение. Подробная ошибка: {err}")
    except Exception as err:
        print(f"Произошла ошибка при попытке логина: {err}")
    
    return False
    

def user_input_change_password() -> None:
    """Меняет пароль пользователя
    """
    try:
        user_login: str = input("Введите логин: ")
        user_new_password: str = input("Введите новый пароль: ")
        server_system.change_password(user_login, user_new_password)
        print("Пароль успешно изменён.")

    except ConnectionError as err:
        print(f"Возникла проблема при подключении к сети. Проверьте своё соединение. Подробная ошибка: {err}")


def main() -> None:
    display_title_screen()
    menu_status: int
    user_input: int
    
    while True:
        if menu_status == 1:
            user_input = menu_address()
            match user_input:
                case 1:
                    if user_input_ip():
                        menu_status = 2
                    break
                
                case 2:
                    sys.exit(0)


        if menu_status == 2:
            user_input = menu_auth()
            match user_input:
                case 1:
                    if user_input_registration():
                        menu_status = 3
                    break
                
                case 2:
                    if user_input_login():
                        menu_status = 3
                    break
        
        
        if menu_status == 3:
            user_input = dm_menu()
            match user_input:
                case 1:
                    sys.exit(0)
                
                case 2:
                    user_input_change_password()
                    break
            
if __name__ == '__main__':
    main()
