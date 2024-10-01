import hashlib
import os
import pickle
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml
from DMBotTools import Color
from PIL import Image, ImageSequence
from systems.file_work import AppPath


class TextureSystem:
    """Статический класс TextureSystem отвечает за управление текстурами, включая их загрузку, изменение цвета, и объединение слоев в одно изображение или GIF.
    """
    __slots__ = []
    DEFAULT_FPS: int = 24
    DEFAULT_COLOR: Color = Color(255, 255, 255, 255)

    @staticmethod
    def _get_hash_list(layers: List[Dict[str, Any]]) -> str:
        """Возвращает хеш списка слоев для идентификации уникальных комбинаций.

        Args:
            layers (List[Dict[str, Any]]): Список слоев.

        Returns:
            str: Хеш в виде строки.
        """
        serialized_data = pickle.dumps(layers)
        hash_object = hashlib.sha256(serialized_data)
        return hash_object.hexdigest()
    
    @staticmethod
    def _slice_image(image: Image.Image, frame_width: int, frame_height: int, num_frames: int) -> List[Image.Image]:
        """Разрезает изображение на кадры заданного размера.

        Args:
            image (Image.Image): Изображение для разрезания.
            frame_width (int): Ширина кадра.
            frame_height (int): Высота кадра.
            num_frames (int): Количество кадров.

        Returns:
            List[Image.Image]: Список кадров.
        """
        frames = []
        image_width, _ = image.size

        for i in range(num_frames):
            row = (i * frame_width) // image_width
            col = (i * frame_width) % image_width
            box = (col, row * frame_height, col + frame_width, row * frame_height + frame_height)
            frame = image.crop(box)
            frame = frame.convert("RGBA")
            frames.append(frame)
        
        return frames

    @staticmethod
    def get_textures(path: str) -> List[Dict[str, Any]]:
        """Загружает текстуры из указанного пути.

        Args:
            path (str): Путь к файлу с текстурами.

        Returns:
            List[Dict[str, Any]]: Список текстур.
        """
        with open(f"{path}/info.yml", 'r') as file:
            info = yaml.safe_load(file)
        
        return info.get('Texture', [])

    @staticmethod
    def get_state_info(path: str, state: str) -> Tuple[int, int, int, bool]:
        """Получает информацию о состоянии текстуры из файла.

        Args:
            path (str): Путь к файлу с текстурами.
            state (str): Имя состояния.

        Raises:
            ValueError: Если информация о состоянии не найдена.

        Returns:
            Tuple[int, int, int, bool]: Ширина кадра, высота кадра, количество кадров и флаг маски.
        """
        with open(f"{path}/info.yml", 'r') as file:
            info = yaml.safe_load(file)
        
        info = info.get('Texture', [])

        sprite_info = next((sprite for sprite in info if sprite['name'] == state), None)
        if not sprite_info:
            raise ValueError(f"No sprite info found for state '{state}' in path '{path}'")
        
        frame_width = sprite_info['size']['x']
        frame_height = sprite_info['size']['y']
        num_frames = sprite_info['frames']
        is_mask = sprite_info['is_mask']

        return frame_width, frame_height, num_frames, is_mask
    
    @staticmethod
    def _get_compiled(path: str, state: str, color: Optional[Color] = None, is_gif: bool = False) -> Union[Image.Image, List[Image.Image], None]:
        """Проверяет наличие компилированного изображения или GIF.

        Args:
            path (str): Путь к файлу.
            state (str): Имя состояния.
            color (Optional[Color], optional): Цвет в формате RGBA. По умолчанию None.
            is_gif (bool, optional): Указывает, является ли изображение GIF. По умолчанию False.

        Returns:
            Union[Image.Image, List[Image.Image], None]: Изображение или список кадров, если существует, иначе None.
        """
        image_path: str = f"{path}/{state}"
        if color:
            image_path += f"_compiled_{color}"
        
        image_path += ".gif" if is_gif else ".png"

        if os.path.exists(image_path):
            with Image.open(image_path) as img:
                if is_gif:
                    return [frame.convert("RGBA").copy() for frame in ImageSequence.Iterator(img)]
                else:
                    return img.convert("RGBA").copy()
        
        else:
            return None
    
    @staticmethod
    def get_image_recolor(path: str, state: str, color: Color = DEFAULT_COLOR) -> Image.Image:
        """Возвращает перекрашенное изображение указанного состояния.

        Args:
            path (str): Путь к файлу.
            state (str): Имя состояния.
            color (Color, optional): Цвет в формате RGBA. По умолчанию DEFAULT_COLOR.

        Returns:
            Image.Image: Перекрашенное изображение.
        """
        image = TextureSystem._get_compiled(path, state, color, False)
        if image:
            return image # type: ignore
        
        with Image.open(f"{path}/{state}.png") as image:
            image = image.convert("RGBA")
            new_colored_image = [
                (
                    int(pixel[0] * color.r / 255),
                    int(pixel[0] * color.g / 255),
                    int(pixel[0] * color.b / 255),
                    pixel[3]
                ) if pixel[3] != 0 else pixel
                for pixel in image.getdata() # type: ignore
            ]

            image.putdata(new_colored_image)
            image.save(f"{path}/{state}_compiled_{color}.png")
            return image
    
    @staticmethod
    def get_image(path: str, state: str) -> Image.Image:
        """Возвращает изображение указанного состояния.

        Args:
            path (str): Путь к файлу.
            state (str): Имя состояния.

        Raises:
            FileNotFoundError: Если файл изображения не найден.

        Returns:
            Image.Image: Изображение состояния.
        """
        image = TextureSystem._get_compiled(path, state, None, False)
        if image:
            return image # type: ignore
        
        raise FileNotFoundError(f"Image file for state '{state}' not found in path '{path}'.")

    @staticmethod
    def get_gif_recolor(path: str, state: str, color: Color = DEFAULT_COLOR, fps: int = DEFAULT_FPS) -> List[Image.Image]:
        """Возвращает перекрашенный GIF указанного состояния.

        Args:
            path (str): Путь к файлу.
            state (str): Имя состояния.
            color (Color, optional): Цвет в формате RGBA. По умолчанию DEFAULT_COLOR.
            fps (int, optional): Частота кадров. По умолчанию DEFAULT_FPS.

        Returns:
            List[Image.Image]: Список кадров перекрашенного GIF.
        """
        image = TextureSystem._get_compiled(path, state, color, True)
        if image:
            return image # type: ignore
        
        image = TextureSystem.get_image_recolor(path, state, color)
        
        frame_width, frame_height, num_frames, _ = TextureSystem.get_state_info(path, state)
        
        frames = TextureSystem._slice_image(image, frame_width, frame_height, num_frames)
        
        output_path = f"{path}/{state}_compiled_{color}.gif"
        frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=1000//fps, loop=0)
        
        return frames
    
    @staticmethod
    def get_gif(path: str, state: str, fps: int = DEFAULT_FPS) -> List[Image.Image]:
        """Возвращает GIF указанного состояния.

        Args:
            path (str): Путь к файлу.
            state (str): Имя состояния.
            fps (int, optional): Частота кадров. По умолчанию DEFAULT_FPS.

        Returns:
            List[Image.Image]: Список кадров GIF.
        """
        image = TextureSystem._get_compiled(path, state, None, True)
        if image:
            return image # type: ignore
        
        image = TextureSystem.get_image(path, state)
        frame_width, frame_height, num_frames, _ = TextureSystem.get_state_info(path, state)
        
        frames = TextureSystem._slice_image(image, frame_width, frame_height, num_frames)
        
        output_path = f"{path}/{state}.gif"
        frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=1000//fps, loop=0)
        
        return frames

    @staticmethod
    def merge_images(background: Image.Image, overlay: Image.Image, position: Tuple[int, int] = (0, 0)) -> Image.Image:
        """Накладывает изображение overlay на изображение background с учетом прозрачности.
        
        Args:
            background (Image.Image): Фоновое изображение.
            overlay (Image.Image): Изображение, которое накладывается.
            position (Tuple[int, int]): Позиция (x, y), куда будет накладываться overlay. По умолчанию (0, 0).

        Returns:
            Image.Image: Объединенное изображение.
        """
        merged_image = background.copy()
        overlay_alpha = overlay.split()[3]
        merged_image.paste(overlay, position, overlay_alpha)
        
        return merged_image

    @staticmethod
    def merge_layers(layers: List[Dict[str, Any]], fps: int = DEFAULT_FPS) -> Union[Image.Image, List[Image.Image]]:
        """Объединяет слои в одно изображение или GIF.

        Args:
            layers (List[Dict[str, Any]]): Список слоев.
            fps (int, optional): Частота кадров для GIF. По умолчанию DEFAULT_FPS.

        Returns:
            Union[Image.Image, List[Image.Image]]: Объединенное изображение или список кадров GIF.
        """
        base_path = os.path.join(AppPath.get_data_path(), 'Compiled')
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        
        hash_layers = TextureSystem._get_hash_list(layers)
        path = os.path.join(base_path, hash_layers)
        
        is_gif: bool = False
        max_width: int = 0
        max_height: int = 0
        max_frames: int = 0
        
        for layer in layers:
            frame_width, frame_height, num_frames, _ = TextureSystem.get_state_info(layer['path'], layer['state'])
            max_width = max(max_width, frame_width)
            max_height = max(max_height, frame_height)
            max_frames = max(max_frames, num_frames)
            if num_frames > 1:
                is_gif = True
        
        path += ".gif" if is_gif else ".png"
        
        if os.path.exists(path):
            with Image.open(path) as img:
                if is_gif:
                    return [frame.convert("RGBA").copy() for frame in ImageSequence.Iterator(img)]
                else:
                    return img.convert("RGBA").copy()

        # Закончили проверку и поняли, что нам надо работать. Первоначальная обработка первого слоя
        final_images: List[Image.Image] = []
        first_layer = layers[0]
        _, _, _, is_mask = TextureSystem.get_state_info(first_layer['path'], first_layer['state'])

        if is_gif:
            if is_mask:
                final_images = [frame for frame in TextureSystem.get_gif_recolor(first_layer['path'], first_layer['state'], first_layer['color'], fps)]
            else:
                final_images = [frame for frame in TextureSystem.get_gif(first_layer['path'], first_layer['state'], fps)]
            
            for i in range(len(final_images)):
                final_image_expanded = Image.new("RGBA", (max_width, max_height))
                final_image_expanded.paste(final_images[i], (0, 0))
                final_images[i] = final_image_expanded
        else:
            if is_mask:
                final_image = TextureSystem.get_image_recolor(first_layer['path'], first_layer['state'], Color(*first_layer['color']))
            else:
                final_image = TextureSystem.get_image(first_layer['path'], first_layer['state'])
            
            final_image_expanded = Image.new("RGBA", (max_width, max_height))
            final_image_expanded.paste(final_image, (0, 0))
            final_images.append(final_image_expanded)

        # Обработка оставшихся слоев
        for layer in layers[1:]:
            _, _, _, is_mask = TextureSystem.get_state_info(layer['path'], layer['state'])

            if is_gif:
                if is_mask:
                    recolored_frames = TextureSystem.get_gif_recolor(layer['path'], layer['state'], Color(*layer['color']), fps)
                    for i in range(max_frames):
                        recolored_frame_expanded = Image.new("RGBA", (max_width, max_height))
                        frame_to_use = recolored_frames[min(i, len(recolored_frames) - 1)]  # Используем последний кадр, если i превышает количество кадров
                        recolored_frame_expanded.paste(frame_to_use, (0, 0))
                        if i < len(final_images):
                            final_images[i] = TextureSystem.merge_images(final_images[i], recolored_frame_expanded)
                        else:
                            final_images.append(recolored_frame_expanded)
                else:
                    normal_frames = TextureSystem.get_gif(layer['path'], layer['state'], fps)
                    for i in range(max_frames):
                        normal_frame_expanded = Image.new("RGBA", (max_width, max_height))
                        frame_to_use = normal_frames[min(i, len(normal_frames) - 1)]  # Используем последний кадр, если i превышает количество кадров
                        normal_frame_expanded.paste(frame_to_use, (0, 0))
                        if i < len(final_images):
                            final_images[i] = TextureSystem.merge_images(final_images[i], normal_frame_expanded)
                        else:
                            final_images.append(normal_frame_expanded)
            else:
                if is_mask:
                    recolored_image = TextureSystem.get_image_recolor(layer['path'], layer['state'], Color(*layer['color']))
                    recolored_image_expanded = Image.new("RGBA", (max_width, max_height))
                    recolored_image_expanded.paste(recolored_image, (0, 0))
                    for i in range(len(final_images)):
                        final_images[i] = TextureSystem.merge_images(final_images[i], recolored_image_expanded)
                else:
                    normal_image = TextureSystem.get_image(layer['path'], layer['state'])
                    normal_image_expanded = Image.new("RGBA", (max_width, max_height))
                    normal_image_expanded.paste(normal_image, (0, 0))
                    for i in range(len(final_images)):
                        final_images[i] = TextureSystem.merge_images(final_images[i], normal_image_expanded)
        
        # Создаем новое изображение с максимальными размерами
        if is_gif:
            final_images[0].save(path, save_all=True, append_images=final_images[1:], duration=1000//fps, loop=0)
            return final_images.copy()
        
        else:
            final_images[0].save(path)
            return final_images[0].copy()
