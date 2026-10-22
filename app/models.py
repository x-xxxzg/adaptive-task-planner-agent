"""数据模型（待按教程填写）。

用途：定义接口的请求/响应结构（Pydantic 模型），
例如任务 Task 的标题、预计时长、优先级等字段。
"""

from pydantic import BaseModel , Field
from datetime import date
from typing import Literal

class TaskCreate(BaseModel):
    title: str = Field(min_length= 1, max_length= 120)
    deadline : date
    estimated_minutes : int = Field(gt = 0,le = 480)
    priority: Literal["low","medium","high"] = "medium" #默认medium

class TaskRead (TaskCreate):
    id: int
    status: Literal["pending","done"] = "pending"




    


