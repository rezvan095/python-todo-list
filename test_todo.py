import pytest
from todo_oop import TaskManager


# --- ФИКСТУРА ---
# Этот блок автоматически создает ЧИСТЫЙ менеджер перед КАЖДЫМ тестом.
# Он гарантирует, что тесты не мешают друг другу.
@pytest.fixture
def manager():
    return TaskManager(db_name=":memory:")


# --- ТЕСТЫ ---

def test_add_task(manager):
    # В начале пусто
    assert len(manager.get_tasks()) == 0

    manager.add_task("Купить хлеб")

    tasks = manager.get_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Купить хлеб"
    assert tasks[0].done is False


def test_mark_done(manager):
    # Добавляем задачу
    manager.add_task("Учить Python")

    # Берем её ID
    task_id = manager.get_tasks()[0].id

    # Отмечаем выполненной
    manager.mark_done(task_id)

    # Проверяем, что статус изменился на True (в базе это 1)
    updated_task = manager.get_tasks()[0]
    assert updated_task.done is True


def test_delete_task(manager):
    # Добавляем задачу
    manager.add_task("Выбросить мусор")
    assert len(manager.get_tasks()) == 1

    # Удаляем её
    task_id = manager.get_tasks()[0].id
    manager.delete_task(task_id)

    # Проверяем, что список снова пуст
    assert len(manager.get_tasks()) == 0