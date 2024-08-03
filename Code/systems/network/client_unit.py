import asyncio
import atexit
import os
import shutil
import zipfile
from typing import Any, Dict, Optional, Tuple

import msgpack
import requests
import websockets
from root_path import ROOT_PATH
from systems.events_system import EventManager
from systems.misc import GlobalClass

class ClientUnit(GlobalClass):
    __slots__ = ['_initialized', '_http_url', '_socket_url', '_session', '_token', '_cur_server_name', '_websocket', '_bg_processing', '_bg_task']
    SOCKET_CHUNK_SIZE: int = 8192
    DEFAULT_DOWNLOAD_CHUNK_SIZE: int = 8192

    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._http_url: str = ""
            self._socket_url: str = ""
            self._session: requests.Session = requests.Session()
            
            self._token: Optional[str] = None
            self._cur_server_name: Optional[str] = None
            
            self._websocket: Optional[websockets.WebSocketClientProtocol] = None
            self._bg_processing: bool = False
            self._bg_task: Optional[asyncio.Task] = None

            atexit.register(self._shutdown)

    # --- Net data --- #
    @staticmethod
    def pack_data(data: Any) -> bytes:
        return msgpack.packb(data)

    @staticmethod
    def unpack_data(data: bytes) -> Any:
        return msgpack.unpackb(data)

    # --- Server API --- #
    def check_server(self, ip: str, port: int = 5000) -> None:
        temp_http_url = f"http://{ip}:{port}"
        response = self._session.get(f"{temp_http_url}/server/check_status", timeout=5)
        response.raise_for_status()

        response_data: dict = response.json()
        if response_data.get("message") == "Server is online":
            server_info: dict = response_data.get("server_info", {})
            self._http_url = temp_http_url
            self._socket_url = f"ws://{ip}:{server_info.get('socket_port')}"
            self._cur_server_name = server_info.get("server_name")

    def download_server_content(self, progress_callback=None) -> None:
        try:
            response = self._session.get(f"{self._http_url}/server/download_server_content", stream=True)
            response.raise_for_status()
        
        except requests.RequestException as e:
            raise RuntimeError(f"Error during HTTP request: {e}")

        archive_path = "content.zip"
        content_dir = os.path.join(ROOT_PATH, 'Content', "Servers", self._cur_server_name)
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        try:
            with open(archive_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=self.DEFAULT_DOWNLOAD_CHUNK_SIZE):
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded_size, total_size)
        
        except IOError as e:
            raise IOError(f"Error saving file: {e}")

        if os.path.exists(content_dir):
            shutil.rmtree(content_dir)

        os.makedirs(content_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(content_dir)
        
        except zipfile.BadZipFile as e:
            raise RuntimeError(f"Error extracting zip file: {e}")
        
        finally:
            os.remove(archive_path)

    # --- Auth API --- #
    def register(self, login: str, password: str) -> None:
        self._auth_request("register", login, password)
        self.login(login, password)

    def login(self, login: str, password: str) -> None:
        token = self._auth_request("login", login, password)["token"]
        self._session.headers.update({"Authorization": token})
        self._token = token

    def logout(self) -> None:
        if self._token:
            response = self._session.post(f"{self._http_url}/auth/logout")
            self._session.headers.update({"Authorization": None})
            response.raise_for_status()

    def _auth_request(self, endpoint: str, login: str, password: str) -> Dict[str, Any]:
        response = self._session.post(f"{self._http_url}/auth/{endpoint}", json={'login': login, 'password': password})
        response.raise_for_status()
        return response.json()

    # --- WebSocket work --- #
    async def connect(self) -> None:
        if not self._token:
            raise ConnectionError("Token is not available. Please log in first.")
        
        self._websocket = await websockets.connect(self._socket_url)
        await self._websocket.send(self._token)
        
        # Wait for token confirmation
        response = await self._websocket.recv()
        if response != "Token accepted":
            raise ConnectionError("Token was not accepted by the server")

    async def disconnect(self) -> None:
        await self.stop_bg_processing()
        if self._websocket:
            await self._websocket.close()
            self._websocket = None

    async def send_data(self, data: Dict[str, Any]) -> None:
        if not self._websocket:
            raise ConnectionError("WebSocket connection is not established")
        packed_data = self.pack_data(data)
        await self._websocket.send(packed_data)

    async def recv_data(self) -> Dict[str, Any]:
        if not self._websocket:
            raise ConnectionError("WebSocket connection is not established")
        response = await self._websocket.recv()
        return self.unpack_data(response)

    # --- Background Processing --- #
    async def start_bg_processing(self) -> None:
        if not self._websocket:
            raise ConnectionError("WebSocket connection is not established")
        if self._bg_processing:
            raise ValueError("Background processing is already running")

        self._bg_processing = True
        self._bg_task = asyncio.create_task(self._bg_receive())

    async def stop_bg_processing(self) -> None:
        if self._bg_processing:
            self._bg_processing = False
            if self._bg_task:
                self._bg_task.cancel()
                await self._bg_task
                self._bg_task = None

    async def _bg_receive(self) -> None:
        ev_manager = EventManager()
        while self._bg_processing:
            try:
                data: dict = await self.recv_data()
                await ev_manager.call_open_event(event_name=data.get('ev_type', None), **data)
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log or handle the exception
                pass

    # --- Cleanup --- #
    async def _shutdown(self) -> None:
        self.logout()
        await self.disconnect()
