#暂定规则后续须调整，睡觉须支持在同天睡觉，除了睡觉的时间，其他事件事件如果冲突，可以提示后选择是否并存

from fastapi import FastAPI , status ,HTTPException
from app.models import TaskCreate , TaskRead,DaySettingInput,FixedEventInput
from app.database import connection, init_db
from datetime import date,time,datetime

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

@app.put("/settings/day")
def save_day_setting(payload: DaySettingInput):
    if payload.available_start >= payload.available_end:
        raise HTTPException(
        status_code=400,
        detail="可用窗口暂不支持跨天；请用固定事件排除不可用的时间段",
    )

    with connection() as conn:
        conn.execute("""
            INSERT INTO day_settings (target_date , available_start , available_end , daily_limit_minutes , break_minutes)
            VALUES(?,?,?,?,?)
                ON CONFLICT(target_date) DO UPDATE SET
                available_start = excluded.available_start,
                available_end = excluded.available_end,
                daily_limit_minutes = excluded.daily_limit_minutes,
                break_minutes = excluded.break_minutes       
            """, 
            (payload.target_date.isoformat(),
            payload.available_start.isoformat(),
            payload.available_end.isoformat(),
            payload.daily_limit_minutes,
            payload.break_minutes))
    return payload

@app.get("/settings/day")
def get_day_setting(target_date: date):
    with connection() as conn:
        row = conn.execute("""
            SELECT target_date , available_start , available_end , daily_limit_minutes , break_minutes
            FROM day_settings
            WHERE target_date = ?
        """,(target_date.isoformat(),)).fetchone()
        if row is None :
            raise HTTPException(status_code=404, detail="该日期没有作息设置")
    return dict(row) #字典才能转为json
        
@app.post("/events",status_code=status.HTTP_201_CREATED)
def create_fixed_event(payload: FixedEventInput):
    with connection() as conn:
        if payload.start_time >= payload.end_time:
            raise HTTPException(status_code=400, detail="结束时间必须晚于开始时间")        

        setting_row = conn.execute("""
            SELECT target_date , available_start , available_end , daily_limit_minutes , break_minutes
            FROM day_settings
            WHERE target_date = ?
        """,(payload.target_date.isoformat(),)).fetchone()

        if setting_row is None:
            raise HTTPException(status_code=400, detail="请先设置该日期的作息设置")

        window_start = time.fromisoformat(setting_row["available_start"])
        window_end = time.fromisoformat(setting_row["available_end"])

        if payload.start_time < window_start or payload.end_time > window_end:
            raise HTTPException(status_code=400,detail=f"事件必须在可用时间窗口内（{window_start.strftime('%H:%M')}–{window_end.strftime('%H:%M')}）",)
        
        conn.execute("""
            INSERT INTO fixed_events (target_date, title, start_time, end_time)
            VALUES(?,?,?,?)
        """,(payload.target_date.isoformat(),
            payload.title,
            payload.start_time.isoformat(),
            payload.end_time.isoformat()))

    return payload

@app.get("/events",response_model=list[FixedEventInput])
def list_fixed_events(target_date: date):
    with connection() as conn:
        rows = conn.execute("""
            SELECT target_date, title, start_time, end_time
            FROM fixed_events
            WHERE target_date = ?
            ORDER BY start_time
        """,(target_date.isoformat(),)).fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="该日期没有事件设置")

    return [FixedEventInput(**dict(row)) for row in rows]


        
        






    
    