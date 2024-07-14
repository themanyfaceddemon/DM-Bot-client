import sys

from console_menu import display_title_screen, dm_menu, menu_address, menu_auth
from server_system_setup import server_system


def user_input_ip() -> bool:
    """Ввод IP пользователем

    Returns:
        bool: True если ip валиден
    """
    try:
        user_ip: str = input("Введите IP сервера: ")
        
        # Защита от дурака. 
        # 127,0/0,1^5000 будет преобразовано в 127.0.0.1:5000
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
    raise NotImplementedError(f"user_input_registration() not implemented yet")

def user_input_login() -> bool:
    raise NotImplementedError(f"user_input_login() not implemented yet")

def user_input_chrange_password() -> None:
    raise NotImplementedError(f"user_input_chrange_password() not implemented yet")

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
                    user_input_chrange_password()
                    break
            
if __name__ == '__main__':
    main()
