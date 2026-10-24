"""排期算法（待按教程填写）。

用途：实现自适应排期逻辑——根据任务剩余量、每日可用时长
与完成情况，动态生成/调整每日计划。
"""
from datetime import date,time,datetime,timedelta

PRIORITY_ORDER = {"high": 0,"medium": 1,"low": 2}

def sort_tasks(tasks):
    return sorted(
        tasks,
        key=lambda task:(
            task["deadline"],
            PRIORITY_ORDER[task["priority"]],
            task["id"],
        ),
    )

def schedule_single_window(tasks, target_date, start_time, end_time,
                           daily_limit_minutes, break_minutes):
    cursor = datetime.combine(target_date, start_time)
    window_end = datetime.combine(target_date, end_time)
    planned = []
    unscheduled = []

    for task in sort_tasks(tasks):
        duration = task["estimated_minutes"]
        task_end = cursor + timedelta(minutes=duration)

        if task_end > window_end:
            unscheduled.append({"task_id": task["id"], "reason": "window_too_short"})
            continue

        planned.append({
            "task_id": task["id"],
            "start": cursor.isoformat(timespec="minutes"),
            "end": task_end.isoformat(timespec="minutes"),
        })
        cursor = task_end

    return {"planned": planned, "unscheduled": unscheduled}


