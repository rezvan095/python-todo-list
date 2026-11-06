import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from todo_oop import TaskManager

# --- НАСТРОЙКА БЕЗОПАСНОСТИ ---
# Загружаем переменные окружения из файла .env
load_dotenv()
# Достаем токен бота из переменной BOT_TOKEN (чтобы не хранить его в коде)
TOKEN = os.getenv('BOT_TOKEN')

# --- ИНИЦИАЛИЗАЦИЯ БОТА ---
# Bot - это сам бот (с его токеном), Dispatcher - "мозг", который ловит сообщения
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создаем менеджер задач (наш класс из todo_oop.py) и сразу загружаем старые задачи
manager = TaskManager()
manager.load_tasks()


# --- СОСТОЯНИЯ (FSM) ---
# Нужны, чтобы бот запоминал, что мы от него ждем.
# Например, бот ждет название задачи, а не ID для удаления.
class Form(StatesGroup):
    waiting_for_task_title = State()


# --- КЛАВИАТУРА (Reply) ---
# Кнопки, которые появляются внизу экрана (вместо клавиатуры телефона)
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Показать задачи")],
        [KeyboardButton(text="➕ Добавить задачу")]
    ],
    resize_keyboard=True  # Делает кнопки аккуратными (под размер текста)
)


# --- ОБРАБОТЧИКИ КОМАНД ---
# Ловит команду /start
@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я твой ToDo-бот. Вот твои кнопки:",
        reply_markup=kb  # Прикрепляем наши кнопки к сообщению
    )


# Ловит нажатие на кнопку "📝 Показать задачи"
@dp.message(F.text == "📝 Показать задачи")
async def show_tasks(message: types.Message):
    if not manager.tasks:
        await message.answer("Список задач пуст.", reply_markup=kb)
        return

    text = "=== ТВОИ ЗАДАЧИ ===\n\n"
    inline_keyboard = []

    # Цикл перебора задач
    for index, task in enumerate(manager.tasks, start=1):
        check = "✅" if task.done else "⏳"
        # Строчка ВНУТРИ цикла (отступ 8 пробелов)
        text += f"{check} {index}. {task.title}\n"

        # Создаем ряд кнопок (тоже ВНУТРИ цикла)
        row = [
            types.InlineKeyboardButton(text=f"✅ {task.title[:15]}", callback_data=f"done_{task.id}"),
            types.InlineKeyboardButton(text=f"❌ {task.title[:15]}", callback_data=f"delete_{task.id}")
        ]
        # Добавляем ряд (ВНУТРИ цикла)
        inline_keyboard.append(row)

    # А эта строчка уже ВНЕ цикла (отступ 4 пробела, как у слова text = ...)
    inline_kb = types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    await message.answer(text, reply_markup=inline_kb)


# Ловит нажатие на кнопку "➕ Добавить задачу"
@dp.message(F.text == "➕ Добавить задачу")
async def add_task_start(message: types.Message, state: FSMContext):
    await message.answer("Введи название новой задачи:", reply_markup=kb)
    # Включаем состояние: теперь бот будет ждать текст для новой задачи
    await state.set_state(Form.waiting_for_task_title)


# Ловит следующее сообщение (уже с названием задачи)
# Сработает ТОЛЬКО если бот находится в состоянии waiting_for_task_title
@dp.message(Form.waiting_for_task_title)
async def add_task_finish(message: types.Message, state: FSMContext):
    # Защита от стикеров/картинок (у них нет текста)
    if message.text is None:
        await message.answer("Пожалуйста, отправь название задачи текстом.", reply_markup=kb)
        return

    title = message.text
    manager.add_task(title)  # Сохраняем задачу в файл через наш класс

    await message.answer(f"Задача «{title}» добавлена!", reply_markup=kb)
    # Сбрасываем состояние, чтобы бот снова слушал только кнопки
    await state.clear()


@dp.callback_query(F.data.startswith("done_"))
async def process_done(callback: types.CallbackQuery):
    # 1. Достаем ID из скрытого сигнала кнопки.
    # Например, если сигнал был "done_16", split("_") разобьет его на ["done", "16"],
    # берем второй элемент [1] ("16") и превращаем в число (int).
    task_id = int(callback.data.split("_")[1])

    # 2. Ищем в списке задач ту, у которой совпадает ID.
    # Нам это нужно, чтобы узнать ее название для красивого сообщения.
    task_title = "Неизвестная задача"  # Значение по умолчанию, если вдруг не найдем
    for t in manager.tasks:
        if t.id == task_id:
            task_title = t.title
            break  # Нашли нужную задачу, дальше искать нет смысла

    # 3. Отмечаем задачу выполненной через наш TaskManager (он сохранит это в JSON)
    manager.mark_done(task_id)

    # 4. Отправляем пользователю красивое сообщение.
    # Используем f-строку, чтобы подставить название задачи.
    await callback.message.answer(
        f"Задача «{task_title}» отмечена выполненной! (Нажми 'Показать задачи', чтобы обновить список)")

    # 5. Обязательный шаг: останавливаем "часики загрузки" на кнопке в Телеграме,
    # иначе кнопка будет висеть в состоянии загрузки вечно.
    await callback.answer()


@dp.callback_query(F.data.startswith("delete_"))
async def process_delete(callback: types.CallbackQuery):
    # 1. Достаем ID из скрытого сигнала (например, из "delete_16" получаем 16)
    task_id = int(callback.data.split("_")[1])

    # 2. Ищем название задачи по ID, чтобы написать его в ответе
    task_title = "Неизвестная задача"
    for t in manager.tasks:
        if t.id == task_id:
            task_title = t.title
            break

    # 3. Удаляем задачу (этот метод также сохраняет изменения в файл)
    manager.delete_task(task_id)

    # 4. Отправляем красивое сообщение с названием
    await callback.message.answer(f"Задача «{task_title}» удалена! (Нажми 'Показать задачи', чтобы обновить список)")

    # 5. Убираем часики загрузки с кнопки
    await callback.answer()


# --- ЗАПУСК ---
async def main():
    print("Бот запущен!")
    # Запускаем бесконечный цикл прослушивания сообщений
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())