from fastapi import FastAPI , status
from app.models import TaskCreate , TaskRead

app = FastAPI(title="自适应任务规划助手")

tasks: list[TaskRead] = []
next_id = 1

@app.get("/health")
def health_check():
    return ({"status":"ok"})

@app.post("/tasks",response_model=TaskRead,status_code = status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    global next_id
    task = TaskRead(id = next_id , **payload.model_dump())  #需要id和和传进来的对象转换未字典，塞进TaskCreate里面
    tasks.append(task)
    next_id += 1
    return task

@app.get("/tasks",response_model=list[TaskRead])
def list_tasks():
    return tasks


























