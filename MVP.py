import json
import os




tasks = []
next_id = 1

def show_menu():
    print()
    print("=== МОИ ЗАДАЧИ ===")
    print("1. Показать задачи")
    print("2. Добавить задачу")
    print("3. Отметить выполненной")
    print("4. Удалить задачу")
    print("5. Выход")

def load_tasks():
    global tasks, next_id
    if not os.path.exists('tasks.json'):
        return

    with open('tasks.json', 'r', encoding='utf-8') as f:
        tasks = json.load(f)

    if tasks:
        next_id = max(task['id'] for task in tasks) + 1
    else:
        next_id = 1


def save_tasks():
    with open('tasks.json', 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def add_task():
    global next_id
    title = input('Название задачи: ')
    task = {
        'id': next_id,
        'title': title,
        'done': False
    }
    tasks.append(task)
    next_id += 1
    save_tasks()
    print(f'Задача добавлена: {title}')

def show_tasks():
    if not tasks:
        print('Список задач пуст.')
        return

    print('\n=== СПИСОК ЗАДАЧ ===')
    for task in tasks:
        check = '[x]' if task['done'] else '[ ]'
        print(f'{task["id"]}. {check} {task["title"]}')


def mark_done():
    task_id = int(input('Введите id задачи: '))

    for task in tasks:
        if task['id'] == task_id:
            task['done'] = True
            print(f'Задача "{task["title"]}" отмечена выполненной')
            save_tasks()
            return

    print('Задача с таким id не найдена.')


def delete_task():
    task_id = int(input("Введите id задачи для удаления: "))

    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            del tasks[i]
            print(f'Задача "{task["title"]}" удалена.')
            save_tasks()
            return
    print("Задача с таким id не найдена.")


def main():
    load_tasks()
    while True:
        show_menu()
        choice = input("Выбери меню: ")

        if choice == '1':
            show_tasks()
        elif choice == '2':
            add_task()
        elif choice == '3':
            mark_done()
        elif choice == '4':
            delete_task()
        elif choice == '5':
            print('Пока!')
            break
        else:
            print('Нет такого пункта, попробуй еще раз.')




main()

