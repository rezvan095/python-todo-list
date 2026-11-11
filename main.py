from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware  # Новый импорт
from todo_oop import TaskManager



# Создаем приложения FastAPI
app = FastAPI(title="Мой ToDo API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Подключаем наш манаджер (он автоматически подцепит базу tasks.db)
manager = TaskManager()


# Pydantic-модель. Она нужна, чтобы FastAPI понимал,
# в каком виде отдавать задачи в интернет (в виде JSON).
class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool


# --- МАРШРУТЫ (ЭНДПОИНТЫ) ---

# Когда пользователь заходит на главную страницу сайта ("/")
@app.get("/")
def read_root():
    return {"message": "Привет! Это мое API для ToDO-листа"}


# Когда пользователь запрашивает список задач ("/tasks")
@app.get("/tasks", response_model=list[TaskResponse])
def get_all_tasks():
    # Берем задачи из базы
    tasks = manager.get_tasks()

    # Превращаем объекты Task в словари (чтобы FastAPI мог сделать из них JSON)
    return [
        {"id": task.id, "title": task.title, "done": task.done}
        for task in tasks
    ]


# --- МОДЕЛЬ ДЛЯ СОЗДАНИЯ ЗАДАЧИ ---
class TaskCreate(BaseModel):
    title: str

# --- ЭНДПОИНТ ДЛЯ СОЗДАНИЯ ---
@app.post("/tasks")
def create_task(task: TaskCreate):
    # Вызываем наш метод из TaskManager
    manager.add_task(task.title)
    return {"message": f"Задача '{task.title}' успешно создана!"}


# --- ЭНДПОИНТ ДЛЯ УДАЛЕНИЯ ---
# {task_id} в пути означает, что мы будем передавать ID прямо в URL (например, /tasks/5)
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    result = manager.delete_task(task_id)
    if result:
        return {"message": f"Задача {task_id} удалена."}
    else:
        return {"error": f"Задача с ID {task_id} не найдена."}


# --- МОДЕЛЬ ДЛЯ ОБНОВЛЕНИЯ ---
class TaskUpdate(BaseModel):
    title: str


# --- ЭНДПОИНТ ДЛЯ ОБНОВЛЕНИЯ (PUT) ---
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    # В нашем TaskManager пока нет метода update_task,
    # поэтому сделаем обновление прямо здесь через SQL-запрос
    manager.cursor.execute("UPDATE tasks SET title = ? WHERE id = ?", (task.title, task_id))
    manager.conn.commit()

    if manager.cursor.rowcount > 0:
        return {"message": f"Задача {task_id} обновлена на '{task.title}'"}
    else:
        return {"error": f"Задача с ID {task_id} не найдена."}



