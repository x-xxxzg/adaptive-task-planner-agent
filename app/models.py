"""数据模型：定义接口的请求/响应结构（Pydantic 模型）。

分两组：
1. 旧的条件收集模型（TaskCreate / TaskRead / DaySettingInput / FixedEventInput）
2. 新的 AI 学习计划模型（PlanRequest / PlanResponse 及其嵌套模型）

新模型的字段形状对应 samples/sample_plan.json，改字段时记得同步改那份样例。
"""

from pydantic import BaseModel , Field, model_validator
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


class GoalInput(BaseModel):
    """一个学习目标：用户要学什么、学多久、什么时候之前学完、有多重要。"""
    title: str = Field(min_length=1, max_length=60)
    total_minutes: int = Field(gt=0, le=10000)
    deadline: date
    priority: Literal["low", "medium", "high"] = "medium"


class PlanRequest(BaseModel):
    """生成计划的请求：一段日期范围 + 每天可用条件 + 若干个学习目标。

    front_load_ratio 是用户可调的「提前完成」强度：
    有富余时，每天最多排到每日上限的这个比例（0.8 = 排到 80%，留 20% 缓冲）。
    想更激进给 1.0，想更保守给 0.5。
    """
    start_date: date
    end_date: date
    available_start: time
    available_end: time
    daily_limit_minutes: int = Field(gt=0, le=720)
    break_minutes: int = Field(ge=0, le=60)
    study_order: Literal["by_priority", "by_deadline"] = "by_priority"
    front_load_ratio: float = Field(default=0.8, gt=0, le=1)
    goals: list[GoalInput] = Field(min_length=1)

    @model_validator(mode="after")
    def check_date_range(self):
        if self.end_date < self.start_date:
            raise ValueError("计划结束日期不能早于开始日期")
        if self.available_end <= self.available_start:
            raise ValueError("每天可用时间段：结束时间必须晚于开始时间")
        return self


class StudyBlock(BaseModel):
    """AI 安排的一个学习时段。"""
    goal_title: str = Field(min_length=1, max_length=60)
    start_time: time
    end_time: time
    minutes: int = Field(gt=0, le=720)
    reason: str = Field(min_length=1, max_length=200)

    @model_validator(mode="after")
    def check_time_range(self):
        if self.end_time <= self.start_time:
            raise ValueError("结束时间必须晚于开始时间")
        start_moment = datetime.combine(date.min, self.start_time)
        end_moment = datetime.combine(date.min, self.end_time)
        actual_minutes = int((end_moment - start_moment).total_seconds() / 60)
        if self.minutes != actual_minutes:
            raise ValueError(
                f"minutes 与起止时间不一致：起止算出来是 {actual_minutes} 分钟"
            )
        return self


class DayPlan(BaseModel):
    """一天的计划：这一天的所有学习时段 + 当天合计分钟数。"""
    plan_date: date
    total_minutes: int = Field(ge=0)
    blocks: list[StudyBlock]

    @model_validator(mode="after")
    def check_total_minutes(self):
        blocks_total = sum(block.minutes for block in self.blocks)
        if self.total_minutes != blocks_total:
            raise ValueError(
                f"total_minutes 与各时段之和不一致：时段合计 {blocks_total} 分钟"
            )
        return self


class UnmetGoal(BaseModel):
    """排不完的目标：还差多少分钟、为什么排不完。"""
    goal_title: str = Field(min_length=1, max_length=60)
    remaining_minutes: int = Field(gt=0)
    reason: str = Field(min_length=1, max_length=200)


class PlanResponse(BaseModel):
    """AI 返回的完整计划。

    unmet_goals = 排不完（硬失败）；warnings = 排得完但很紧（软提示）。两者性质不同，分开存。
    """
    daily_plans: list[DayPlan]
    unmet_goals: list[UnmetGoal] = []
    warnings: list[str] = []
