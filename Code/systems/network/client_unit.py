import asyncio
import socket
from typing import Any, Dict, Optional, Tuple

import msgpack
import requests
from systems.decorators import global_class
from systems.events_system import EventManager


@global_class
class ClientUnit:
    __slots__ = ['_http_url', '_socket_url', '_session', '_token', '_socket', '_bg_processing', '_bg_task']
    DEFAULT_DOWNLOAD_CHUNK_SIZE: int = 8192
    
    def __init__(self) -> None:
        self._http_url: str = ""
        self._socket_url: Tuple[str, int] = ("", 0)
        self._session: requests.Session = requests.Session()
        self._token: Optional[str] = None
        self._socket: Optional[socket.socket] = None
        self._bg_processing: bool = False
        self._bg_task: Optional[asyncio.Task] = None
    
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

    def recv_data(self, buffer: int = 8192) -> Dict[str, Any]:
        if self._socket is None:
            raise ConnectionError("Socket connection is not established")
        
        response = self._socket.recv(buffer)
        return ClientUnit.unpack_data(response)
    
    async def bg_receive(self) -> None:
        ev_manager: EventManager = EventManager.get_instance()
        
        while self._bg_processing:
            data: dict = await asyncio.get_event_loop().run_in_executor(None, self.recv_data)
            await ev_manager.call_event(event_name=data.get('ev_type', None), **data)
    
    def start_bg_processing(self) -> None:
        if self._socket is None:
            raise ConnectionError("Socket connection is not established")
        
        if self._bg_processing:
            raise ValueError("Background processing is already running")
        
        self._bg_processing = True
        self._bg_task = asyncio.create_task(self.bg_receive())

    def stop_bg_processing(self) -> None:
        if self._bg_processing:
            self._bg_processing = False
            if self._bg_task is not None:
                self._bg_task.cancel()
                self._bg_task = None
        
    def disconnect(self) -> None:
        self.stop_bg_processing()
        
        if self._socket is not None:
            self._socket.close()
            self._socket = None
