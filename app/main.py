from fastapi import FastAPI , status
from app.models import TaskCreate , TaskRead
from app.database import connection, init_db

app = FastAPI(title="自适应任务规划助手")

init_db()

@app.get("/health")
def health_check():
    return ({"status":"ok"})

@app.post("/tasks",response_model=TaskRead,status_code = status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    with connection() as conn:
        cursor = conn.execute("""
            INSERT INTO tasks (title,deadline,estimated_minutes,priority)
            VALUES(?,?,?,?)""",
            (payload.title,payload.deadline.isoformat(),payload.estimated_minutes,payload.priority)
       )
        task_id = cursor.lastrowid
    return TaskRead(id=task_id,**payload.model_dump())

@app.get("/tasks",response_model=list[TaskRead])
def list_tasks():
    with connection() as conn:
        rows = conn.execute("""
                SELECT id , title, deadline, estimated_minutes, priority, status FROM tasks ORDER BY deadline ,id
        """).fetchall()
    return [TaskRead(**dict(row)) for row in rows]

