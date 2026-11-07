import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Импортируем наш менеджер, который теперь работает с SQLite
from todo_oop import TaskManager

# --- НАСТРОЙКА БЕЗОПАСНОСТИ ---
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# --- ИНИЦИАЛИЗАЦИЯ ---
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создаем менеджер. При его создании (в методе __init__)
# автоматически произойдет подключение к базе данных tasks.db
manager = TaskManager()


# --- СОСТОЯНИЯ (FSM) ---
# Бот должен помнить, что мы от него ждем текст для новой задачи
class Form(StatesGroup):
    waiting_for_task_title = State()


# --- КЛАВИАТУРА ---
# Кнопки внизу экрана
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Показать задачи")],
        [KeyboardButton(text="➕ Добавить задачу")]
    ],
    resize_keyboard=True
)


# --- ОБРАБОТЧИКИ ---

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я твой ToDo-бот. Вот твои кнопки:",
        reply_markup=kb
    )


@dp.message(F.text == "📝 Показать задачи")
async def show_tasks(message: types.Message):
    # ВАЖНО: Берем задачи не из списка в памяти (как было с JSON),
    # а делаем SQL-запрос к базе данных через метод get_tasks()
    tasks = manager.get_tasks()

    # Если база вернула пустой список
    if not tasks:
        await message.answer("Список задач пуст.", reply_markup=kb)
        return

    text = "=== ТВОИ ЗАДАЧИ ===\n\n"
    inline_keyboard = []

    # Перебираем задачи из базы. index - для красивого вывода (1, 2, 3), task - сам объект
    for index, task in enumerate(tasks, start=1):
        check = "✅" if task.done else "⏳"
        text += f"{check} {index}. {task.title}\n"

        # Создаем кнопки. В callback_data передаем РЕАЛЬНЫЙ ID из базы (task.id)
        row = [
            types.InlineKeyboardButton(text=f"✅ {task.title[:15]}", callback_data=f"done_{task.id}"),
            types.InlineKeyboardButton(text=f"❌ {task.title[:15]}", callback_data=f"delete_{task.id}")
        ]
        inline_keyboard.append(row)

    inline_kb = types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    await message.answer(text, reply_markup=inline_kb)


@dp.message(F.text == "➕ Добавить задачу")
async def add_task_start(message: types.Message, state: FSMContext):
    await message.answer("Введи название новой задачи:", reply_markup=kb)
    # Говорим боту: "Теперь жди текст, это будет название задачи"
    await state.set_state(Form.waiting_for_task_title)


@dp.message(Form.waiting_for_task_title)
async def add_task_finish(message: types.Message, state: FSMContext):
    # Защита от картинок и стикеров (у них нет текста)
    if message.text is None:
        await message.answer("Пожалуйста, отправь название задачи текстом.", reply_markup=kb)
        return

    title = message.text
    # Вызываем метод добавления (внутри него выполнится SQL-запрос INSERT)
    manager.add_task(title)

    await message.answer(f"Задача «{title}» добавлена!", reply_markup=kb)
    # Сбрасываем состояние ожидания
    await state.clear()


@dp.callback_query(F.data.startswith("done_"))
async def process_done(callback: types.CallbackQuery):
    # Достаем ID задачи из скрытого сигнала кнопки (например, из "done_5" получаем 5)
    task_id = int(callback.data.split("_")[1])

    # Чтобы написать красивое сообщение, нам нужно имя задачи.
    # Мы снова запрашиваем актуальный список из базы и ищем нужный ID
    tasks = manager.get_tasks()
    task_title = "Неизвестная задача"
    for t in tasks:
        if t.id == task_id:
            task_title = t.title
            break

    # Выполняем SQL-запрос UPDATE (отметить выполненной)
    manager.mark_done(task_id)

    await callback.message.answer(f"Задача «{task_title}» отмечена выполненной! (Нажми 'Показать задачи')")
    # Убираем "часики" загрузки с кнопки
    await callback.answer()


@dp.callback_query(F.data.startswith("delete_"))
async def process_delete(callback: types.CallbackQuery):
    # Достаем ID из сигнала удаления
    task_id = int(callback.data.split("_")[1])

    # Ищем название для красивого сообщения
    tasks = manager.get_tasks()
    task_title = "Неизвестная задача"
    for t in tasks:
        if t.id == task_id:
            task_title = t.title
            break

    # Выполняем SQL-запрос DELETE (удалить задачу)
    manager.delete_task(task_id)

    await callback.message.answer(f"Задача «{task_title}» удалена! (Нажми 'Показать задачи')")
    await callback.answer()


# --- ЗАПУСК ---
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())