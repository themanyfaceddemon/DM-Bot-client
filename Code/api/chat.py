from typing import List, Literal, Optional

import dearpygui.dearpygui as dpg
import dpg_tools
from DMBotNetwork import Client
from systems.loc import Localization as loc


class ChatMessageType:
    __slots__ = ["_message_type", "message", "sender"]

    def __init__(
        self,
        message_type: Literal["ooc", "admin"],
        message: str,
        sender: Optional[str] = None,
    ) -> None:
        self._message_type: str = message_type
        self.message: str = message
        self.sender: Optional[str] = sender

    @property
    def message_type(self) -> str:
        return self._message_type

    @message_type.setter
    def message_type(self, value: Literal["ooc", "admin"]) -> None:
        self._message_type = value


class ChatClientModule:
    messages: List[ChatMessageType] = []
    filters = {"ooc": True, "admin": True}
    current_chat_type: str = "ooc"  # Текущий выбранный чат по умолчанию

    @staticmethod
    async def send_chat_message(chat_message_type: ChatMessageType) -> None:
        """Отправляет сообщение через сеть."""
        await Client.req_net_func(
            "send_message",
            message=chat_message_type.message,
            message_type=chat_message_type.message_type,
        )

    @staticmethod
    async def net_get_chat_message(
        message: str, message_type: str, sender: Optional[str] = None
    ) -> None:
        """Получает сообщение и добавляет его в чат."""
        ChatClientModule.messages.append(ChatMessageType(message_type, message, sender))  # type: ignore
        ChatClientModule.update_chat_display()

    @classmethod
    async def _iternal_send_message(cls, sender, app_data, user_data) -> None:
        """Асинхронная отправка сообщения через UI."""
        raw_message = dpg_tools.decode_string(dpg.get_value("chat_input"))
        message_type = dpg.get_value("chat_type_selector")
        chat_message = ChatMessageType(message_type, raw_message.strip())  # type: ignore
        await cls.send_chat_message(chat_message)
        dpg.set_value("chat_input", "")

    @classmethod
    def create_window(cls, sender, app_data, user_data):
        """Создание основного окна чата с фильтрацией и отправкой сообщений."""
        if dpg.does_item_exist("chat_window"):
            dpg.focus_item("chat_window")
            return

        with dpg.window(
            label=loc.get_string("chat_window_lable"),
            tag="chat_window",
            width=400,
            height=400,
        ):
            with dpg.menu_bar():
                with dpg.menu(label=loc.get_string("chat_filter")):
                    dpg.add_menu_item(
                        label="OOC",
                        callback=cls.update_filter,
                        user_data="ooc",
                        check=True,
                        default_value=True,
                    )
                    dpg.add_menu_item(
                        label="Admin",
                        callback=cls.update_filter,
                        user_data="admin",
                        check=True,
                        default_value=True,
                    )

            dpg.add_child_window(
                label="Chat Display", autosize_x=True, height=200, tag="chat_display"
            )

            with dpg.group(horizontal=True):
                dpg.add_combo(
                    items=["ooc", "admin"],
                    default_value="ooc",
                    tag="chat_type_selector",
                    width=80,
                )

                dpg.add_input_text(
                    width=270,
                    tag="chat_input",
                    hint=loc.get_string("chat_input_hint"),
                    on_enter=True,
                    callback=cls._iternal_send_message,
                )

            dpg.add_key_press_handler(
                parent="main_registry", callback=cls.key_press_callback
            )

    @classmethod
    def key_press_callback(cls, sender, app_data):
        """Обрабатывает нажатие клавиш."""
        if app_data == ord("T"):  # TODO Сделать ебаные настройки уже
            dpg.focus_item("chat_input")

    @classmethod
    def update_filter(cls, sender, app_data, user_data):
        """Обновляет фильтры в зависимости от состояния чекбоксов."""
        cls.filters[user_data] = app_data
        cls.update_chat_display()

    @classmethod
    def update_chat_display(cls):
        """Обновляет отображение сообщений в чате на основе фильтров."""
        dpg.delete_item("chat_display", children_only=True)

        for chat_message in cls.messages:
            if cls.filters[chat_message.message_type]:
                display_message = f"[{chat_message.message_type}] {chat_message.sender}: {chat_message.message}"
                dpg.add_text(display_message, parent="chat_display", wrap=0)
