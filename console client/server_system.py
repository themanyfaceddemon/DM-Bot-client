import os
import requests


class ServerSystem:
    __slots__ = ['_session', '_ip']
    DEFAULT_CHUNK_SIZE: int = 8192
    
    def __init__(self) -> None:
        self._session = requests.Session()
        self._ip: str = ""
    
    def setup_server_ip(self, ip: str) -> None:
        """Устанавливает IP-адрес сервера и проверяет его доступность.

        Args:
            ip (str): IP-адрес сервера.

        Raises:
            ConnectionError: Если сервер недоступен.
        """
        if not self.check_connect(ip):
            raise ConnectionError(f"Unable to connect to server at {ip}")
        
        self._ip = ip
    
    def check_connect(self, ip: str) -> bool:
        """Проверяет доступность сервера.

        Args:
            ip (str): IP-адрес сервера.

        Returns:
            bool: True, если сервер доступен (ответил с кодом 200), иначе False.
        """
        response = self._session.get(f"http://{ip}/server/status")
        if response.status_code == 200:
            return True
        
        return False

    def download_server_texture(self) -> str:
        """Загружает текстуры с сервера.

        Returns:
            str: Путь до архива с текстурами.

        Raises:
            requests.exceptions.HTTPError: Если запрос к серверу завершился ошибкой.
            IOError: Если произошла ошибка при сохранении файла.
        """
        response: requests.Response = self._session.post(f"http://{self._ip}/server/download", stream=True)
        response.raise_for_status()

        archive_path = "sprites.zip"

        try:
            with open(archive_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=self.DEFAULT_CHUNK_SIZE):
                    file.write(chunk)
        
        except IOError as e:
            raise IOError(f"Error saving file: {e}")

        return os.path.abspath(archive_path)

    def register(self, login: str, password: str) -> None:
        """Регистрация пользователя на сервере.

        Args:
            login (str): Логин пользователя.
            password (str): Пароль пользователя.

        Raises:
            ValueError: Если в ответе сервера отсутствует токен.
            requests.exceptions.HTTPError: Если запрос к серверу завершился ошибкой.
        """
        payload = {
            "login": login,
            "password": password
        }
        
        response: requests.Response = self._session.post(f"http://{self._ip}/account/register", json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if "token" in data:
            self._session.headers.update({"user_token": data["token"]})
            return
        
        raise ValueError("Token not found in response")

    def login(self, login: str, password: str) -> None:
        """Авторизация пользователя на сервере.

        Args:
            login (str): Логин пользователя.
            password (str): Пароль пользователя.

        Raises:
            ValueError: Если в ответе сервера отсутствует токен.
            requests.exceptions.HTTPError: Если запрос к серверу завершился ошибкой.
        """
        payload = {
            "login": login,
            "password": password
        }
        
        response: requests.Response = self._session.post(f"http://{self._ip}/account/login", json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if "token" in data:
            self._session.headers.update({"user_token": data["token"]})
            return
        
        raise ValueError("Token not found in response")

    def logout(self) -> None:
        """Выход пользователя из системы.

        Raises:
            requests.exceptions.HTTPError: Если запрос к серверу завершился ошибкой.
        """
        response: requests.Response = self._session.post(f"http://{self._ip}/account/logout")
        response.raise_for_status()
