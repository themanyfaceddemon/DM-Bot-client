import logging

logger = logging.getLogger("Test ev")

#TODO: Удалить после добавления первого нормального ивента

def test_echo(data): # Ивенты работают только по именованным аргументам! Если сервер отправил data, то и в функцию прийдёт только data. socket_user, socket_access: UserAccess всегда можно поставить в функцию
    logger.info(f"Echo event called with data: {data}")
    
test_echo.event_name = "echo" # Указание типа ивента
