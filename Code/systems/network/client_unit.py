import asyncio
import logging
import socket
from typing import Any, Dict, Optional, Tuple

import msgpack
import requests

logger = logging.getLogger("Client Unit")

class ClientUnit:
    DEFAULT_CHUNK_SIZE: int = 8192
    
    def __init__(self) -> None:
        self._http_url: str = ""
        self._socket_url: Tuple[str, int] = ("", 0)
        self._session: requests.Session = requests.Session()
        self._token: Optional[str] = None
        self._socket: Optional[socket.socket] = None
    
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
    
    # --- Socket work --- #
    def connect(self) -> None:
        if self._token is None:
            raise ConnectionError("Token is not available. Please log in first.")
        
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(self._socket_url)
        logger.info(f"Connected to server at {self._socket_url}")
        
        self._socket.sendall(self._token.encode('utf-8'))
        
        # Ждем подтверждения токена
        response = self._socket.recv(1024)
        if response != b"Token accepted":
            raise ConnectionError("Token was not accepted by the server")

    def send_data(self, data: Dict[str, Any]) -> None:
        if self._socket is None:
            raise ConnectionError("Socket connection is not established")
        
        packed_data = ClientUnit.pack_data(data)
        self._socket.sendall(packed_data)
        logger.debug(f"Sent data: {data}")

    def disconnect(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None
