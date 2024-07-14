from art import tprint


def menu_address():
    print("\n1. Ввести адрес")
    print("2. Завершить программу\n")
    print("Введите действие: ", end="")


def menu_auth():
    print("\n1. Зарегистрироваться")
    print("2. Авторизоваться")
    print("3. Выйти\n")
    print("Введите действие: ", end="")

def dm_menu():
    print("\n1. Выйти с системы")
    print("2. Сменить пароль\n")
    print("Введите действие: ", end="")


def display_title_screen():
    tprint("DM_bot_client")
    print('')
