import os
import pickle

class BinaryFileSystem:
    def __init__(self, file_path):
        """Инициализирует объект BinaryFileSystem.

        Args:
        file_path (str): Путь к файлу.
        """
        self._file_path = os.path.abspath(file_path)
        if os.path.exists(self._file_path):
            with open(self._file_path, 'rb') as f:
                self._data = pickle.load(f)
        else:
            self._data = {}

    def __getitem__(self, key):
        """Возвращает значение по ключу.

        Args:
        key (str): Ключ для доступа к значению.

        Returns:
        object: Значение, соответствующее ключу.
        """
        return self._data.get(key, None)

    def __setitem__(self, key, value):
        """Устанавливает значение по ключу и сохраняет изменения в файл, если значение отличается от текущего.

        Args:
        key (str): Ключ для установки значения.
        value (object): Устанавливаемое значение.
        """
        if key in self._data and self._data[key] == value:
            return  # Не записываем, если значение не изменилось
        self._data[key] = value
        self._write_to_file()

    def __del__(self):
        """Сохраняет данные в файл при удалении объекта."""
        self._write_to_file()

    def _write_to_file(self):
        """Записывает данные в файл."""
        with open(self._file_path, 'wb') as f:
            pickle.dump(self._data, f)