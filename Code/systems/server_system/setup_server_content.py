import os
import zipfile

from root_path import ROOT_PATH
from main_impt import server_system


def setup_server_content() -> None:
    """Проверяет наличие папки Sprites в корневом каталоге. При отсутствии- вызывает функцию server_system.download_server_texture() и распаковывает архив по пути результата этой функции. Удаялет архив после этого.
    """
    
    sprites_dir = os.path.join(ROOT_PATH, 'Sprites')
    
    if not os.path.exists(sprites_dir):
        zip_path = server_system.download_server_texture()
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(sprites_dir)

        os.remove(zip_path)
