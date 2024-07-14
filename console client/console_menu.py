from art import tprint


def menu_address():
    print("\n1. Ввести адрес")
    print("2. Завершить программу\n")
    choice = int(input("Введите действие: "))
    return choice

def menu_auth():
    print("\n1. Зарегистрироваться")
    print("2. Авторизоваться")
    print("3. Выйти\n")
    choice = int(input("Введите действие: "))
    return choice

def dm_menu():
    print("\n1. Выйти с системы")
    print("2. Сменить пароль\n")
    choice = int(input("Введите действие: "))
    return choice


def display_title_screen():
    tprint("DM bot client")
    print('')
