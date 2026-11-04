import json
import os
from random import choice


class Task:
    def __init__(self, task_id, title, done=False):
        self.id = task_id
        self.title = title
        self.done = done


    def __str__(self):
        check = "[x]" if self.done else "[ ]"
        return f"{self.id}. {check} {self.title}"


    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done
        }


class TaskManager:
    def __init__(self):
        self.tasks = []
        self.next_id = 1

    def add_task(self, title):
        mew_task = Task(self.next_id, title)
        self.tasks.append(mew_task)
        self.next_id += 1
        print(f'Задача "{title}" добавлена')
        self.save_task()


    def show_tasks(self):
        if not self.tasks:
            print("Список задач пуст.")
            return

        print("\n=== СПИСОК ЗАДАЧ ===")
        for task in self.tasks:
            print(task)


    def mark_done(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                task.done = True
                print(f'Задача "{task.title}" отмечена выполненной.')
                self.save_task()
                return
            print("Задача с таким id не найдена")

    def delete_task(self, task_id):
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                print(f'Задача "{task.title}" удалена.')
                self.save_task()
                return
            print("Задача с таким id не найдена.")


    def save_task(self):
        data = [task.to_dict() for task in self.tasks]
        with open('tasks.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


    def load_tasks(self):
        if not os.path.exists("tasks.json"):
            return

        with open('tasks.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.tasks = []
        for item in data:
            task = Task(item["id"], item["title"], item["done"])
            self.tasks.append(task)

        if self.tasks:
            self.next_id = max(task.id for task in self.tasks) + 1



def main():

    manager = TaskManager()
    manager.load_tasks()


    while True:
        print("\n=== МОИ ЗАДАЧИ ===")
        print("1. Показать задачи")
        print("2. Добавить задачу")
        print("3. Отметить выполненной")
        print("4. Удалить задачу")
        print("5. Выход")

        choice = input("Выбери меня: ")

        if choice == "1":
            manager.show_tasks()
        elif choice == "2":
            title = input('Название задачи: ')
            manager.add_task(title)
        elif choice == "3":
            task_id = int(input("Введите id задачи: "))
            manager.mark_done(task_id)
        elif choice == "4":
            task_id = int(input('Введите id задачи для удаления: '))
            manager.delete_task(task_id)
        elif choice == "5":
            print('Пока!')
            break
        else:
            print('Нет такого пункта, попробуйте еще раз.')

if __name__ == '__main__':
    main()