from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить таблетку"),
         KeyboardButton(text="Список моих таблеток"),
         KeyboardButton(text="Удалить таблетку")]
    ],
    resize_keyboard=True
)

def confirm_keyboard(pill_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Принял",
        callback_data=f'confirm_{pill_id}'
    )
    return builder.as_markup()

def delete_keyboard(pills: list):
    builder = InlineKeyboardBuilder()
    for pill in pills:
        builder.button(
            text=f'❌   {pill.name}',
            callback_data=f'delete_{pill.id}'
        )
    builder.adjust(1)
    return builder.as_markup()
