"""给大模型用的提示词。

三条设计决定：

1. **拆成 system / user 两个函数**：真接 API 时 system 只发一次，user 每轮都发。
   而且重试要把上一轮的错误塞进 user 消息，所以必须是函数而不是常量字符串。
2. **指令用英文**：同样意思比中文省一半以上 token。
   但 reason / warnings 是给用户看的，明确要求用中文输出。
3. **容量由代码算好再交给 AI**：需求、富余这些算术一律在 plan_validator 里算完，
   AI 只负责「怎么分配到每天」这种需要权衡的事。
"""

from app.models import PlanRequest
from app.plan_validator import calculate_capacity


def build_plan_system_prompt() -> str:
    """生成会话的 system 消息：角色、规则、输出格式。整个会话只发一次。"""
    return """You are a study scheduling engine. Output JSON only, no prose, no markdown fence.

RULES
1. Each goal's scheduled minutes must equal its total_minutes exactly.
2. No block may fall after that goal's deadline.
3. Sum of a day's blocks must not exceed the daily limit.
4. Every block must lie inside the daily window.
5. Blocks in one day must not overlap; leave at least the required gap between them.
6. A goal that cannot be fully scheduled goes into "unmet_goals" with remaining_minutes and a reason.
7. Follow the CAPACITY strategy given in the user message.
8. Write "reason" and "warnings" in Chinese. All other values must match the input exactly.

OUTPUT FORMAT (single-line JSON)
{"daily_plans":[{"plan_date":"YYYY-MM-DD","total_minutes":0,"blocks":[{"goal_title":"","start_time":"HH:MM:SS","end_time":"HH:MM:SS","minutes":0,"reason":""}]}],"unmet_goals":[],"warnings":[]}
"""


def build_plan_user_message(request: PlanRequest, previous_issues: list[str] | None = None) -> str:
    """生成会话的 user 消息：条件、目标、富余策略，重试时追加上一轮的问题。"""
    goal_lines = "\n".join(
        f"- {goal.title}: {goal.total_minutes} min, "
        f"deadline {goal.deadline}, priority {goal.priority}"
        for goal in request.goals
    )

    capacity = calculate_capacity(request)
    ratio_percent = int(request.front_load_ratio * 100)
    front_load_minutes = int(request.daily_limit_minutes * request.front_load_ratio)

    if capacity["is_tight"]:
        strategy = (
            "No slack. Do NOT front-load; spread across the full range. "
            'Add a Chinese note to "warnings" explaining the time pressure.'
        )
    else:
        strategy = (
            f"Slack available. Front-load: fill each day up to ~{front_load_minutes} min "
            f"({ratio_percent}% of the daily limit) so goals finish early, "
            "leaving buffer for later days."
        )

    message = f"""WINDOW
- range: {request.start_date} .. {request.end_date}
- daily window: {request.available_start}-{request.available_end}
- daily limit: {request.daily_limit_minutes} min/day
- gap between blocks: >= {request.break_minutes} min
- order within a day: {request.study_order}

GOALS
{goal_lines}

CAPACITY
- demand {capacity['total_demand']} min / capacity {capacity['total_capacity']} min, slack {capacity['surplus_days']} day(s)
- {strategy}
"""

    if not previous_issues:
        return message

    issue_lines = "\n".join(f"- {issue}" for issue in previous_issues)
    return message + f"""
PREVIOUS OUTPUT HAD THESE PROBLEMS - FIX THEM
{issue_lines}

Output the complete JSON again, not just the changed part.
"""
