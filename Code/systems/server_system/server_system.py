import atexit
import os
import requests
from root_path import ROOT_PATH
import zipfile
import shutil


class AccessError(Exception):
    """Ошибка доступа. Возникает, когда сервер возвращает статус код 403, что указывает на отсутствие прав доступа к ресурсу.
    
    Args:
        Exception (тип): Базовый класс для всех встроенных исключений.
    """
    pass

class InternalServerError(Exception):
    """Внутренняя ошибка сервера. Возникает, когда сервер возвращает статус код 500, что указывает на внутреннюю ошибку на сервере.
    
    Args:
        Exception (тип): Базовый класс для всех встроенных исключений.
    """
    pass

class ServerSystem:
    __slots__ = ['_session', '_url']
    DEFAULT_CHUNK_SIZE: int = 8192

    def __init__(self) -> None:
        """Инициализирует объект ServerSystem, создавая сессию и устанавливая URL сервера.
        """
        self._session = requests.Session()
        self._url: str = "http://"
        atexit.register(self.logout)
    
    @staticmethod
    def _code_error_processing(response: requests.Response) -> None:
        """Обрабатывает ошибки на основе статус-кода ответа сервера.

        Args:
            response (requests.Response): Ответ от сервера.

        Raises:
            AccessError: Если статус-код ответа 403.
            InternalServerError: Если статус-код ответа 500.
        """
        if response.status_code == 403:
            raise AccessError()
        
        if response.status_code == 500:
            raise InternalServerError(response.json().get("error", ""))          
    
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
        return response.status_code == 200

    def download_server_texture(self) -> None:
        """Загружает текстуры с сервера. 

        Raises:
            requests.exceptions.HTTPError: Если запрос к серверу завершился ошибкой.
            IOError: Если произошла ошибка при сохранении файла.
        """
        response: requests.Response = self._session.post(f"{self._url}/server/download", stream=True)
        ServerSystem._code_error_processing(response)

        archive_path = "sprites.zip"
        sprites_dir = os.path.join(ROOT_PATH, 'Sprites')

        try:
            with open(archive_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=self.DEFAULT_CHUNK_SIZE):
                    file.write(chunk)
        
        except IOError as e:
            raise IOError(f"Error saving file: {e}")

        if os.path.exists(sprites_dir):
            shutil.rmtree(sprites_dir)

        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(sprites_dir)

        os.remove(archive_path)


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
        ServerSystem._code_error_processing(response)

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
        ServerSystem._code_error_processing(response)

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
        ServerSystem._code_error_processing(response)

    def logout(self) -> None:
        """Выход пользователя из системы.

        Raises:
            requests.exceptions.HTTPError: Если запрос к серверу завершился ошибкой.
        """
        response: requests.Response = self._session.post(f"{self._url}/account/logout")
        ServerSystem._code_error_processing(response)
