import atexit
import json
from pathlib import Path
from typing import Any, Dict

from .app_path import AppPath


class Settings:
    _settings_data: Dict[str, Any] = {}
    _path: Path = Path(AppPath.get_data_path() / "main_app_settings.json")
    __slots__ = []

    @classmethod
    def load(cls) -> None:
        cls._settings_data = {}
        cls._load_settings()

        atexit.register(cls._save_settings)

    @classmethod
    def _load_settings(cls) -> None:
        if cls._path.exists():
            with open(cls._path, "r", encoding="utf-8") as file:
                cls._settings_data = json.load(file)

        else:
            cls._settings_data = {}

    @classmethod
    def _save_settings(cls) -> None:
        cls._path.parent.mkdir(parents=True, exist_ok=True)
        with open(cls._path, "w", encoding="utf-8") as file:
            json.dump(
                cls._settings_data, file, ensure_ascii=False, indent=4, sort_keys=True
            )

    @classmethod
    def _update_nested_dict(
        cls, original: Dict[str, Any], updates: Dict[str, Any]
    ) -> None:
        for key, value in updates.items():
            if isinstance(value, dict):
                original[key] = original.get(key, {})
                cls._update_nested_dict(original[key], value)
            else:
                if key not in original:
                    original[key] = value

    @classmethod
    def init_base_settings(cls, base_settings: Dict[str, Any]) -> None:
        if not cls._settings_data:
            cls._settings_data = base_settings
        else:
            cls._update_nested_dict(cls._settings_data, base_settings)

        cls._save_settings()

    @classmethod
    def get_s(cls, key: str) -> Any:
        keys = key.split(".")
        data = cls._settings_data
        for k in keys:
            if not isinstance(data, dict) or k not in data:
                return None
            data = data[k]

        return data

    @classmethod
    def set_s(cls, key: str, value: Any) -> None:
        keys = key.split(".")
        data = cls._settings_data
        for k in keys[:-1]:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]

        data[keys[-1]] = value

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        return cls._settings_data
