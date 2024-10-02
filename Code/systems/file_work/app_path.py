from pathlib import Path

from DMBotNetwork import Client


class AppPath:
    _root_path = Path(__file__).parents[3]
    _client_path = _root_path / "Content" / "Client"
    _data_path = _root_path / "data"
    _servers_path = _root_path / "Content" / "Servers"
    _cur_server_path = _servers_path

    @classmethod
    def get_root(cls) -> Path:
        return cls._root_path

    @classmethod
    def get_client_path(cls) -> Path:
        return cls._client_path

    @classmethod
    def get_data_path(cls) -> Path:
        return cls._data_path

    @classmethod
    def get_servers_path(cls) -> Path:
        return cls._servers_path

    @classmethod
    def get_cur_server_path(cls) -> Path:
        return cls._cur_server_path

    @classmethod
    def update_cur_server_name(cls) -> None:
        cls._cur_server_path = cls._servers_path / Client.get_server_name()
        cls._cur_server_path.mkdir(parents=True, exist_ok=True)
