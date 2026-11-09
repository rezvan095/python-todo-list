import pytest
from todo_oop import TaskManager


# --- ФИКСТУРА ---
@pytest.fixture
def manager():
    return TaskManager(db_name=":memory:")


# --- ТЕСТЫ ---

def test_add_task(manager):
    assert len(manager.get_tasks()) == 0
    manager.add_task("Купить хлеб")
    tasks = manager.get_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Купить хлеб"
    assert tasks[0].done is False


def test_mark_done(manager):
    manager.add_task("Учить Python")
    task_id = manager.get_tasks()[0].id
    manager.mark_done(task_id)
    updated_task = manager.get_tasks()[0]
    assert updated_task.done is True


def test_delete_task(manager):
    manager.add_task("Выбросить мусор")
    assert len(manager.get_tasks()) == 1
    task_id = manager.get_tasks()[0].id
    manager.delete_task(task_id)
    assert len(manager.get_tasks()) == 0


# --- НОВЫЙ ТЕСТ (добавлен в конец) ---
def test_delete_nonexistent_task(manager):
    manager.add_task("Реальная задача")

    # Пытаемся удалить несуществующую задачу (ID 999)
    result = manager.delete_task(999)

    # Проверяем, что метод вернул False (так как ничего не удалил)
    assert result is False

    # Проверяем, что реальная задача осталась цела
    tasks = manager.get_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Реальная задача"