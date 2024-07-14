from art import tprint


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
    tprint("DM bot client")
    print('')
