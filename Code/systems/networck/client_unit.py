import asyncio
import os
import shutil
import zipfile
from typing import Any, Dict, Optional

import msgpack
import requests
import websockets
from root_path import ROOT_PATH
from systems.decorators import global_class
from systems.events import EventManager


@global_class
class ClientUnit:
    __slots__ = ['_ip', '_session', '_token', '_websocket', '_running']
    DEFAULT_CHUNK_SIZE: int = 8192
    
    def __init__(self, ip: str) -> None:
        self._ip: str = ip
        self.check_ip()
        
        self._session: requests.Session = requests.Session()
        self._token: Optional[str] = None
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._running: bool = False
    
    # --- Net data --- #
    @staticmethod
    def pack_data(data: Any) -> bytes:
        return msgpack.packb(data)
    
    @staticmethod
    def unpack_data(data: bytes) -> Any:
        return msgpack.unpackb(data, raw=False)

    # --- Server API --- #
    def check_ip(self) -> bool:
        response = self._session.get(f"http://{self._ip}/server/check_status")
        return response.status_code == 200
    
    def download_server_content(self) -> None:
        response = self._session.post(f"http://{self._ip}/server/download_server_content", stream=True)

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
        response = self._session.post(f"http://{self._ip}/auth/register", json={'login': login, 'password': password})
        
        response.raise_for_status()
        
        if response.status_code == 200:
            self.login(login, password)
    
    def login(self, login: str, password: str) -> None:
        response = self._session.post(f"http://{self._ip}/auth/login", json={'login': login, 'password': password})
        
        response.raise_for_status()
        
        if response.status_code == 200:
            token = response.json()["token"]
            self._session.headers.update({"Authorization": token})
            self._token = token

    # --- Admin API --- #
    def change_password(self, new_password: str) -> None:
        response = self._session.post(f"http://{self._ip}/admin/change_password", json={'new_password': new_password})
        response.raise_for_status()
    
    def change_access(self, login: str, new_access: Dict[str, bool]) -> None:
        response = self._session.post(f"http://{self._ip}/admin/change_access", json={'login': login, 'new_access': new_access})
        response.raise_for_status()
    
    def delete_user(self, login: str) -> None:
        response = self._session.post(f"http://{self._ip}/admin/delete_user", json={'login': login})
        response.raise_for_status()
    
    # --- WebSocket work --- #
    async def connect(self) -> None:
        if self._token is None:
            raise ConnectionError("Token is not available. Please log in first.")
        
        self._websocket = await websockets.connect(f"ws://{self._ip}/connect", extra_headers={"Authorization": self._token})

    async def send_data(self, data: Dict[str, Any]) -> None:
        if self._websocket is None:
            raise ConnectionError("WebSocket connection is not established")
        
        packed_data = ClientUnit.pack_data(data)
        await self._websocket.send(packed_data)

    async def _handle_data(self) -> None:
        event_manager = EventManager()
        
        try:
            while self._running:
                response = await self._websocket.recv()
                decoded_response = ClientUnit.unpack_data(response)
                event_type = decoded_response.get("ev_type")

                await event_manager.call_event(event_type, **decoded_response)
        
        except websockets.ConnectionClosed:
            pass
        
        finally:
            self._running = False
    
    def handle_data(self) -> None:
        if self._websocket is None:
            raise ConnectionError("WebSocket connection is not established")
        
        if self._running:
            raise ValueError("handle_data already started")
        
        self._running = True
        asyncio.create_task(self._handle_data())
        
    async def disconnect(self) -> None:
        self._running = False
        if self._websocket is not None:
            await self._websocket.close()
            self._websocket = None
