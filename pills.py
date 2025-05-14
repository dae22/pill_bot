import re
from sqlalchemy import select, func
from aiogram import Router, Bot, F, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime, time, timedelta
from keyboard import *
from database import AsyncSessionLocal, PillOrm


router = Router()

class AddPillStates(StatesGroup):
    entering_name = State()
    entering_time = State()

class DeletePillStates(StatesGroup):
    selecting_pill = State()

@router.message(F.text == "Добавить таблетку")
async def add_pill_start(message: Message, state: FSMContext):
    await state.set_state(AddPillStates.entering_name)
    await message.answer("Введите название лекарства:")

@router.message(AddPillStates.entering_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddPillStates.entering_time)
    await message.answer("Введите время приема в формате ЧЧ:ММ:")

@router.message(AddPillStates.entering_time)
async def process_time(message: Message, state: FSMContext):
    if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', message.text):
        await message.answer("Неверный формат времени! Введите снова:")
        return
    try:
        hours, minutes = map(int, message.text.split(':'))
        time_obj = time(hour=hours, minute=minutes)
    except ValueError:
        await message.answer("Некорректное время! Введите снова:")
        return

    data = await state.get_data()
    await state.clear()

    async with AsyncSessionLocal() as session:
        new_pill = PillOrm(user_id=message.from_user.id, name=data['name'], time=time_obj)
        session.add(new_pill)
        await session.commit()
        await message.answer(f"✅ {data['name']} добавлено на {message.text}", reply_markup=main_keyboard)

@router.message(F.text == "Удалить таблетку")
async def delete_pill(message: Message, state: FSMContext):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PillOrm).where(PillOrm.user_id == message.from_user.id)
        )
        pills = list(result.scalars().all())

    if not pills:
        await message.answer("У вас нет добавленных таблеток")
        return
    await state.set_state(DeletePillStates.selecting_pill)
    await message.answer("Выберите лекарство для удаления:", reply_markup=delete_keyboard(pills))

@router.message(F.text == "Список моих таблеток")
async def list_pills(message: Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PillOrm).where(PillOrm.user_id == message.from_user.id)
        )
        pills = list(result.scalars().all())

    if not pills:
        await message.answer("У вас нет добавленных лекарств")
        return

    response = "Ваши лекарства:\n" + "\n".join(
        [f"💊 {pill.name} - {pill.time.strftime('%H:%M')}" for pill in pills]
    )
    await message.answer(response)

@router.callback_query(F.data.startswith("confirm_"))
async def confirm_pill(callback: types.CallbackQuery):
    pill_id = int(callback.data.split("_")[1])
    async with AsyncSessionLocal() as session:
        pill = await session.get(PillOrm, pill_id)
        if pill and (pill.last_taken is None or pill.last_taken < datetime.now().date()):
            pill.last_taken = datetime.now().date()
            await session.commit()
            await callback.message.edit_text(
                f"✅ Прием {pill.name} подтверждён",
                reply_markup=None
            )
            await callback.answer()

@router.callback_query(F.data.startswith('delete_'), DeletePillStates.selecting_pill)
async def delete_pill_handler(callback: types.CallbackQuery, state: FSMContext):
    pill_id = int(callback.data.split("_")[1])
    async with AsyncSessionLocal() as session:
        pill = await session.get(PillOrm, pill_id)
        if pill:
            await session.delete(pill)
            await session.commit()
            await callback.message.edit_text(f'✅ {pill.name} удален')
    await state.clear()

async def check_pills(bot: Bot):
    now = datetime.now().time().replace(second=0, microsecond=0)
    current_date = datetime.now().date()
    async with AsyncSessionLocal() as session:
        stmt = select(PillOrm).where(
            (PillOrm.time <= now) &
            ((PillOrm.last_taken.is_(None)) | (PillOrm.last_taken < current_date)) &
            ((PillOrm.last_notified.is_(None)) | (PillOrm.last_notified <= datetime.now() - timedelta(minutes=10)))
        )
        result = await session.execute(stmt)
        pills = result.scalars().all()

        for pill in pills:
            await bot.send_message(
                pill.user_id,
                f"⏰ Пора принять {pill.name}!",
                reply_markup=confirm_keyboard(pill.id)
            )
            pill.last_notified = datetime.now()
            await session.commit()