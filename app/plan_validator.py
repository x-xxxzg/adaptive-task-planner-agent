"""计划校验与容量计算。

这里只放「代码能算明白的」东西：
- calculate_capacity()：算需求 / 容量 / 富余，供提示词和可行性判断使用
- check_feasibility()、validate_plan()：下一步加

原则：能算的别问 AI。AI 只负责「怎么分配到每天」这种需要权衡的事，
「排不排得下」「还剩多少富余」这类算术一律由这里给出精确数字。
"""

from app.models import PlanRequest


def calculate_capacity(request: PlanRequest) -> dict:
    """算出需求、容量和富余，供提示词使用。

    返回的键：
        total_days      计划总天数
        total_capacity  总容量（分钟）
        total_demand    总需求（分钟）
        surplus_minutes 富余（分钟），负数表示排不下
        surplus_days    富余折算成天
        is_tight        是否紧张（富余不足 1 天）
    """
    total_days = (request.end_date - request.start_date).days + 1
    total_capacity = total_days * request.daily_limit_minutes
    total_demand = sum(goal.total_minutes for goal in request.goals)
    surplus_minutes = total_capacity - total_demand
    surplus_days = surplus_minutes // request.daily_limit_minutes
    if surplus_minutes < 0:
        surplus_text = f"缺口{abs(surplus_minutes)}分钟"
    else:
        surplus_text = f"富余{surplus_minutes}分钟,（约{surplus_days}天）"
    return {
        "total_days": total_days,
        "total_capacity": total_capacity,
        "total_demand": total_demand,
        "surplus_minutes": surplus_minutes,
        "surplus_days": surplus_days,
        "is_tight": surplus_days < 1,
        "summary": f"计划{total_days}天，每天上限{request.daily_limit_minutes}分钟，总容量{total_capacity}分钟；目标总需求{total_demand}分钟，"+surplus_text
    }
