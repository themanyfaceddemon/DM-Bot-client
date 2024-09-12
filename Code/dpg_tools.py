import asyncio
import inspect
import sys

import dearpygui.dearpygui as dpg


def decode_string(instr: str):
    """Данную функцию нужно вызывать каждый раз при получении данных от пользователя (input_text). Винда у нас особая и не работает по нормальному. Язык стола зачарований из майна нам не нужен (и тот который блять на винде только)"""
    if not sys.platform == "win32":  # Иди нахуй винда
        return instr

    translation_table = str.maketrans(
        {chr(i): chr(i + 0x350) for i in range(0x00C0, 0x100)}
    )

    translation_table.update({0x00B8: chr(0x0451), 0x00A8: chr(0x0401)})

    return instr.translate(translation_table)


def add_timer(interval, callback, repeat_count=None, *args, **kwargs):
    is_coroutine = inspect.iscoroutinefunction(callback)
    task = asyncio.create_task(
        _repeating_timer(
            interval, callback, is_coroutine, repeat_count, *args, **kwargs
        )
    )
    return task


async def _repeating_timer(
    interval, callback, is_coroutine, repeat_count=None, *args, **kwargs
):
    counter = 0
    while dpg.is_dearpygui_running() and (
        repeat_count is None or counter < repeat_count
    ):
        await asyncio.sleep(interval)
        if is_coroutine:
            await callback(*args, **kwargs)
        else:
            callback(*args, **kwargs)
        counter += 1
