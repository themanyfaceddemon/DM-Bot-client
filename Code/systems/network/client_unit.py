import asyncio
import logging
import os
import shutil
import socket
import zipfile
from typing import Any, Dict, Optional, Tuple

import msgpack
import requests
from root_path import ROOT_PATH
from systems.decorators import global_class
from systems.events import EventManager


logger = logging.getLogger("Client Unit")

@global_class
class ClientUnit:
    __slots__ = ['_http_url', '_socket_url', '_session', '_token', '_socket', '_running']
    DEFAULT_CHUNK_SIZE: int = 8192
    
    def __init__(self) -> None:
        self._http_url: str
        self._socket_url: Tuple[str, int]
        
        self._session: requests.Session = requests.Session()
        self._token: Optional[str] = None
        self._socket: Optional[socket.socket] = None
        self._running: bool = False
    
    # --- Net data --- #
    @staticmethod
    def pack_data(data: Any) -> bytes:
        return msgpack.packb(data)
    
    @staticmethod
    def unpack_data(data: bytes) -> Any:
        return msgpack.unpackb(data, raw=False)

    # --- Server API --- #
    def check_server(self, ip: str, port: int = 5000, socket_port: int = 5001) -> bool:
        self._http_url = f"http://{ip}:{port}"
        self._socket_url = (ip, socket_port)
        
        response = self._session.get(f"{self._http_url}/server/check_status")
        response.raise_for_status()
        
        return response.status_code == 200
    
    def download_server_content(self) -> None:
        response = self._session.get(f"{self._http_url}/server/download_server_content", stream=True)

        archive_path = "content.zip"
        content_dir = os.path.join(ROOT_PATH, 'Content')

        try:
            with open(archive_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=self.DEFAULT_CHUNK_SIZE):
                    file.write(chunk)
        
        except IOError as e:
            raise IOError(f"Error saving file: {e}")

        if os.path.exists(content_dir):
            shutil.rmtree(content_dir)

        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(content_dir)

        os.remove(archive_path)
    
    # --- Auth API --- #
    def register(self, login: str, password: str) -> None:
        response = self._session.post(f"{self._http_url}/auth/register", json={'login': login, 'password': password})
        
        response.raise_for_status()
        
        if response.status_code == 200:
            self.login(login, password)
    
    def login(self, login: str, password: str) -> None:
        response = self._session.post(f"{self._http_url}/auth/login", json={'login': login, 'password': password})
        
        response.raise_for_status()
        
        if response.status_code == 200:
            token = response.json()["token"]
            self._session.headers.update({"Authorization": token})
            self._token = token

    def logout(self) -> None:
        response = self._session.post(f"{self._http_url}/auth/logout")
        self._session.headers.update({"Authorization": None})
        response.raise_for_status()
    
    # --- Admin API --- #
    def change_password(self, new_password: str) -> None:
        response = self._session.post(f"{self._http_url}/admin/change_password", json={'new_password': new_password})
        response.raise_for_status()
    
    def change_access(self, login: str, new_access: Dict[str, bool]) -> None:
        response = self._session.post(f"{self._http_url}/admin/change_access", json={'login': login, 'new_access': new_access})
        response.raise_for_status()
    
    def delete_user(self, login: str) -> None:
        response = self._session.post(f"{self._http_url}/admin/delete_user", json={'login': login})
        response.raise_for_status()
    
    # --- Socket work --- #
    def connect(self) -> None:
        if self._token is None:
            raise ConnectionError("Token is not available. Please log in first.")
        
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(self._socket_url)
        
        self._socket.sendall(self._token.encode('utf-8'))

    def send_data(self, data: Dict[str, Any]) -> None:
        if self._socket is None:
            raise ConnectionError("Socket connection is not established")
        
        packed_data = ClientUnit.pack_data(data)
        self._socket.sendall(packed_data)

    def handle_data(self) -> None:
        if self._token is None:
            raise ConnectionError("Token is not available. Please log in first.")
        
        if self._running:
            raise ValueError("handle_data already started")
        
        self._running = True
        asyncio.create_task(self._handle_data())

    async def _handle_data(self) -> None:
        event_manager = EventManager()
        
        try:
            while self._running:
                response = self._socket.recv(1024)
                if not response:
                    break
                
                decoded_response: dict = ClientUnit.unpack_data(response)
                event_type = decoded_response.get("ev_type")

                await event_manager.call_event(event_type, **decoded_response)
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        
        finally:
            self.disconnect()
        
    def disconnect(self) -> None:
        self._running = False
        if self._socket is not None:
            self._socket.close()
            self._socket = None
