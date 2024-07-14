import requests
import console_menu
import supp_module  # Предполагается, что у вас есть файл supp_module.py
import pickle

ip = ""
url = ""
credentials_file = 'credentials.ctgf'
bin_file = "data_info.bin"
data = {
    "ip": "gg",
    "login": "aga",
    "password": "1234"
}


def main() -> None:
    console_menu.display_title_screen()
    while True:
        # 1. Ввод адреса или выход
        console_menu.menu_address()
        choice = int(input())
        if choice == 1:
            # Ввод IP-адреса
            ip = str(input("Введите IP: "))
            url = f"http://{ip}"
            response = requests.get(url + "/server/status")  # Предполагается, что endpoint "/status" доступен
            if response.status_code == 200:
                print("Соединение установлено.")
                print(response.json())
                data["ip"] = ip
                with open(bin_file, "wb") as f:
                    pickle.dump(data, f)
                    print("Адрес сохранен!")
            else:
                print(f"Ошибка: {response.status_code}")
                continue
        elif choice == 2:
            # Выход
            exit()
        else:
            print("Введено неверное действие!")
            continue

        # 2. Регистрация, вход или выход
        while True:
            console_menu.menu_auth()
            choice = int(input())
            if choice == 1:
                # Регистрация
                supp_module.register(url)  # Предполагается, что в supp_module.py есть функция register()
                break
            elif choice == 2:
                # Вход
                supp_module.login(url)  # Предполагается, что в supp_module.py есть функция login()
                break
            elif choice == 3:
                # Выход
                break
            else:
                print("Введено неверное действие!")

        # 3. Меню действий (только после успешного входа)
        if choice == 2:
            while True:
                console_menu.dm_menu()
                choice = int(input())
                if choice == 1:
                    # Смена пароля
                    supp_module.change_password(url)  # Предполагается, что в supp_module.py есть функция change_password()
                elif choice == 2:
                    # Выход из учетной записи
                    break
                else:
                    print("Введено неверное действие!")

    # end main
    pass


if __name__ == '__main__':
    main()