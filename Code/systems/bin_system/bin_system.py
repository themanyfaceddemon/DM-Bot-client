import atexit
import os
import pickle
from typing import Any, Dict, Optional

from root_path import ROOT_PATH


class BinaryFileSystem:
    __slots__ = ['_data', '_file_path']
    
    def __init__(self, file_path: Optional[str], file_name: str) -> None:
        """Инициализирует объект BinaryFileSystem.
        На текущий момент данный класс используется как сохранение настроек

        Args:
            file_path (Optional[str]): Путь до файла с данными
            file_name (str): Имя файла
        """
        if not file_path:
            file_path = ""
        
        full_file_path = os.path.join(ROOT_PATH, "data", full_file_path)
        
        if not os.path.exists(full_file_path):
            os.makedirs(full_file_path)
        
        self._file_path = os.path.join(full_file_path, f"{file_name}.bin")
        
        self._data = {}
        try:
            self._read_file()
        
        except Exception:
            self._write_file()
        
        atexit.register(self._write_file)

    def _write_file(self) -> None:
        """Записывает данные в файл.
        """
        with open(self._file_path, 'wb') as file:
            pickle.dump(self._data, file)
    
    def _read_file(self) -> Dict[str, Any]:
        """Читает данные из файла

        Returns:
            Dict[str, Any]: Словарь данных
        """
        with open(self._file_path, 'rb') as file:
            self._data = pickle.load(file)

    def __getitem__(self, key) -> Any:
        """Возвращает значение по ключу.

        Args:
            key (str): Ключ для доступа к значению.

        Returns:
            Any: Значение, соответствующее ключу.
        """
        return self._data.get(key, None)

    def __setitem__(self, key: str, value: Any) -> None:
        """Устанавливает значение по ключу и сохраняет изменения в файл, если значение отличается от текущего.

        Args:
            key (str): Ключ для установки значения.
            value (Any): Устанавливаемое значение.
        """
        if key in self._data and self._data.get(key, None) == value:
            return
        
        self._data[key] = value
        self._write_file()
