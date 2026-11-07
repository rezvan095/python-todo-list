import sqlite3


class Task:
    def __init__(self, task_id, title, done=False):
        self.id = task_id
        self.title = title
        self.done = done

    def __str__(self):
        check = "[x]" if self.done else "[ ]"
        return f"{self.id}. {check} {self.title}"


class TaskManager:
    def __init__(self):
        # Подключаемся к базе данных
        self.conn = sqlite3.connect("tasks.db")
        # Чтобы можно было обращаться к полям по имени (row["title"])
        self.conn.row_factory = sqlite3.Row
        # ВОТ ОНО - создание того самого cursor, на который ругается PyCharm
        self.cursor = self.conn.cursor()

        # Создаем таблицу, если ее нет
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        self.conn.commit()

    def get_tasks(self):
        # Достаем все задачи из базы и превращаем их в объекты Task
        self.cursor.execute("SELECT * FROM tasks")
        rows = self.cursor.fetchall()
        return [Task(row["id"], row["title"], bool(row["done"])) for row in rows]

    def add_task(self, title):
        self.cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title, False))
        self.conn.commit()
        print(f'Задача "{title}" добавлена.')

    def show_tasks(self):
        # Используем get_tasks для вывода в консоль (если запустим отдельно)
        tasks = self.get_tasks()
        if not tasks:
            print("Список задач пуст.")
            return

        print("\n=== СПИСОК ЗАДАЧ ===")
        for task in tasks:
            print(task)

    def mark_done(self, task_id):
        self.cursor.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
        self.conn.commit()
        print(f'Задача {task_id} отмечена выполненной.')

    def delete_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
        print(f'Задача {task_id} удалена.')