import requests


class ServerSystem:
    def __init__(self) -> None:
        self._session = requests.Session()
        self._ip: str = ""
        
    def check_connect(self) -> bool:
        """Функция проверки доступности сервера

        Returns:
            bool: True если сервер прислал нужный ответ
        """
        response = self._session.get(f"http://{self._ip}/server/status")
        if response.status_code == 200:
            return True
        
        return False

    def register(self, login: str, password: str) -> str:
        pass