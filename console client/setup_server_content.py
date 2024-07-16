import os
import zipfile
from server_system_setup import server_system
from root_path import ROOT_PATH


def setup_server_content() -> None:
    """Проверяет наличие папки Sprites в корневом каталоге. При отсутствии- вызывает функцию server_system.download_server_texture() и распаковывает архив по пути результата этой функции. Удаялет архив после этого.
    """
    
    root_dir = ROOT_PATH
    sprites_dir = os.path.join(root_dir, 'Sprites')
    
    if not os.path.exists(sprites_dir):
        zip_path = server_system.download_server_texture()
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(sprites_dir)

        os.remove(zip_path)
