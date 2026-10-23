"""数据模型（待按教程填写）。

用途：定义接口的请求/响应结构（Pydantic 模型），
例如任务 Task 的标题、预计时长、优先级等字段。
"""

from pydantic import BaseModel , Field
from datetime import date,time,datetime,timedelta,timezone
from typing import Literal

class TaskCreate(BaseModel):
    title: str = Field(min_length= 1, max_length= 120)
    deadline: date
    estimated_minutes: int = Field(gt = 0,le = 480)
    priority: Literal["low","medium","high"] = "medium" #默认medium

class TaskRead (TaskCreate):
    id: int
    status: Literal["pending","done"] = "pending"

class DaySettingInput(BaseModel):
    target_date: date 
    available_start: time
    available_end: time
    daily_limit_minutes: int = Field(gt = 0, le = 720)
    break_minutes: int = Field(ge = 0, le = 60)

class FixedEventInput(BaseModel):
    target_date: date
    title: str = Field(min_length=1, max_length=100)
    start_time: time
    end_time: time
