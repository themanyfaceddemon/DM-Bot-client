import os

import requests


class ServerSystem:
    __slots__ = ['_session', '_url']
    DEFAULT_CHUNK_SIZE: int = 8192
    
    def __init__(self) -> None:
        self._session = requests.Session()
        self._url: str = "http://"
        
    def __del__(self):
        self.logout()
    
    def setup_server_ip(self, ip: str) -> None:
        """Устанавливает IP-адрес сервера и проверяет его доступность.

        Args:
            ip (str): IP-адрес сервера.

        Raises:
            ConnectionError: Если сервер недоступен.
        """
        if not self.check_connect(ip):
            raise ConnectionError(f"Unable to connect to server at {ip}")
        
        self._url = f"http://{ip}"
    
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
        response: requests.Response = self._session.post(f"{self._url}/server/download", stream=True)
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
        
        response: requests.Response = self._session.post(f"{self._url}/account/register", json=payload)
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
        
        response: requests.Response = self._session.post(f"{self._url}/account/login", json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if "token" in data:
            self._session.headers.update({"user_token": data["token"]})
            return
        
        raise ValueError("Token not found in response")


    def change_password(self, login: str, new_password: str) -> None:
        """Изменяет пароль пользователя.

        Args:
            login (str): Логин пользователя, чей пароль будет изменен.
            new_password (str): Новый пароль для пользователя.

        Raises:
            requests.exceptions.HTTPError: При возникновении HTTP ошибки.
            requests.exceptions.RequestException: При возникновении ошибки запроса.
        """
        payload = {
            "login": login,
            "new_password": new_password
        }
        
        response: requests.Response = self._session.post(f"{self._url}/account/change_user_password", json=payload)
        response.raise_for_status()

    def logout(self) -> None:
        """Выход пользователя из системы.

        Raises:
            requests.exceptions.HTTPError: Если запрос к серверу завершился ошибкой.
        """
        response: requests.Response = self._session.post(f"{self._url}/account/logout")
        response.raise_for_status()
