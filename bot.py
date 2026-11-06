import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from todo_oop import TaskManager

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')


bot = Bot(token=TOKEN)
dp = Dispatcher()


manager = TaskManager()
manager.load_tasks()


class Form(StatesGroup):
    waiting_for_task_title = State()
    waiting_for_done_id = State()
    waiting_for_delete_id = State()



kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Показать задачи")],
        [KeyboardButton(text="➕ Добавить задачу")],
        [KeyboardButton(text="✅ Отметить выполненной")],
        [KeyboardButton(text="❌ Удалить задачу")]
    ],
    resize_keyboard=True
)


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я твой ToDo-бот. Вот твои кнопки:",
        reply_markup=kb
    )


@dp.message(F.text == "📝 Показать задачи")
async def show_tasks(message: types.Message):
    if not manager.tasks:
        await message.answer("Список задач пуст.")
        return

    text = "=== ТВОИ ЗАДАЧИ ===\n\n"
    for task in manager.tasks:
        check = "✅" if task.done else "⏳"
        text += f"{check} {task.id}. {task.title}\n"

    await message.answer(text)


@dp.message(F.text == "➕ Добавить задачу")
async def add_task_start(message: types.Message, state: FSMContext):
    await message.answer("Введи название новой задачи:")
    await state.set_state(Form.waiting_for_task_title)


@dp.message(Form.waiting_for_task_title)
async def add_task_finish(message: types.Message, state: FSMContext):
    if message.text is None:
        await message.answer("Пожалуйста, отправь название задачи текстом.", reply_markup=kb)
        return


    title = message.text
    manager.add_task(title)

    await message.answer(f"Задача «{title}» добавлена!", reply_markup=kb)
    await state.clear()


@dp.message(F.text == "✅ Отметить выполненной")
async def mark_done_start(message: types.Message, state: FSMContext):
    await message.answer("Введите ID задачи, которую нужно отметить:")
    await state.set_state(Form.waiting_for_done_id)


@dp.message(Form.waiting_for_done_id)
async def mark_done_finish(message: types.Message, state: FSMContext):
    if message.text is None:
        await message.answer("Пожалуйста, отправь ID числом (текстом).", reply_markup=kb)
        return

    try:
        task_id = int(message.text)
        manager.mark_done(task_id)
        await message.answer(f'Готово! Проверь список.')
    except ValueError:
        await message.answer("Ошибка! Нужно ввести число (ID задачи)")
    await state.clear()


@dp.message(F.text == "❌ Удалить задачу")
async def delete_task_start(message: types.Message, state: FSMContext):
    await message.answer("Введи ID задачи, которую нужно удалить:")
    await state.set_state(Form.waiting_for_delete_id)

@dp.message(Form.waiting_for_delete_id)
async def delete_task_finish(message: types.Message, state: FSMContext):
    if message.text is None:
        await message.answer("Пожалуйста, отправь ID числом (текстом).", reply_markup=kb)
        return

    try:
        task_id = int(message.text)
        manager.delete_task(task_id)
        await message.answer(f'Задача с ID {task_id} успешно удалена!', reply_markup=kb)
    except ValueError:
        await message.answer("Ошибка! Нужно ввести число (ID задачи).", reply_markup=kb)
    await state.clear()

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
