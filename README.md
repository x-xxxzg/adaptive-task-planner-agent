# 自适应学习计划生成助手（Adaptive Task Planner Agent）

> 核心定位：**AI 生成安排，软件负责收集条件、保存、校验和展示；以后再根据执行反馈让 AI 重排。**
> 用 FastAPI 提供接口，把用户的目标与可用时间交给大模型，再把 AI 返回的结构化计划校验后展示出来。

## 项目功能说明

本项目面向有多个学习目标的学生。用户输入目标名称、所需总学习时长、完成期限和优先级，并设置计划日期范围、每天可学习的时间段、每日学习时长上限及个人偏好的学习顺序。系统将这些信息发送给大模型，由 AI 生成按日期排列的学习计划，再将计划展示给用户。

例如，用户可以同时设置"11 月 1 日前完成 30 小时英语学习"和"11 月 10 日前完成 40 小时语文学习"。系统允许两个目标在同一段日期内同时推进；如果同一天安排了两个目标，则根据用户设置的优先级安排先后。

用户可以查看计划中的日期、学习目标、开始和结束时间、时长及安排理由。用户修改了可用时间、目标期限或优先级后，可以请求 AI 重新生成计划。后续版本支持用户标记学习时段已完成、部分完成或延期，并让 AI 根据剩余目标和最新时间安排重新规划未完成部分。

系统不会让 AI 的回复直接成为计划。后端会检查返回的数据格式和基本约束，例如：学习时段是否在用户可用时间内、目标是否超过期限、每天总时长是否超限、时段是否冲突，以及同一天的目标顺序是否符合优先级。若计划不满足条件，系统提示用户调整条件或重新生成。

## 两个入口

用户可以用两种方式提出需求。两条路**最终汇合成同一份结构化数据（`PlanRequest`）**，后面的代码完全共用，不需要写两遍。

| 入口 | 用户输入 | 需要 AI 吗 | 说明 |
| --- | --- | --- | --- |
| 结构化表单 | 自己填目标、时长、截止日期、优先级、每天可用时间 | 不需要 | 数据本来就是结构化的，代码可以直接判断 |
| 一句话 | 「12 月前考四级，每天晚上能学两小时」 | 需要 | AI 先把自然语言**抽取**成结构化条件 |

一句话入口抽取完成后，要把读出来的条件**展示给用户确认**再继续。这一步如果失败，多半不是条件真冲突，而是 AI 理解错了用户的话——让人看一眼比让 AI 重试更省事。

> **原则：能算的别问 AI，需要权衡的才交给 AI。**
>
> 没有结构化数据时（一句话、语音），AI 的价值是「把非结构化变成结构化」，这一步代码做不了；
> 一旦变成结构化数据，立刻切回代码——「排不排得完」是算术，「怎么分配到每天」才是权衡。

## 计划生成流程

```text
用户输入
   ↓
PlanRequest（结构化条件）      ← 两个入口在这里汇合
   ↓
check_feasibility  可行性检查 · 代码算
   ├─ 不可行 → 直接告诉用户哪里不可能，不让 AI 白跑
   └─ 可行 ↓
AI 出计划
   ↓
validate_plan  校验 6 条约束 · 代码算
   ├─ 通过   → 返回计划
   ├─ 不通过 → 把错误清单塞回提示词，让 AI 重出（最多 3 轮）
   └─ 3 轮都错 → 返回最后一份问题清单
```

**重试必须带反馈**：只把原提示词重发一遍，AI 大概率犯同一个错。要把上一轮 `validate_plan` 报出的具体问题写进提示词，重试才有意义。

## 校验分工

| 位置 | 判什么 | 时机 | 返回 |
| --- | --- | --- | --- |
| `models.py` 的 `@model_validator` | 单个对象**内部**自洽 | 数据一进来 | 422 |
| `check_feasibility()` | 用户提的条件自己说得通吗（纯算术） | 交给 AI **之前** | 问题清单 |
| `validate_plan()` | AI 的作业做对了吗（要对照 `PlanRequest`） | AI 返回**之后** | 问题清单 |

**划分依据：只看一个对象自己就能判的 → `@model_validator`；要比较两个以上对象、或要对照用户要求的 → `validate_plan`。**

`models.py` 已实现的 5 条：

| 模型 | 检查 |
| --- | --- |
| `PlanRequest` | `end_date >= start_date`；`available_end > available_start` |
| `StudyBlock` | `end_time > start_time`；`minutes` 必须等于起止时间算出的分钟数 |
| `DayPlan` | `total_minutes` 必须等于各时段之和 |

`validate_plan()` 要检查的 6 条：时段是否在可用时间内、是否超过目标截止日、是否超过每日上限、同一天时段是否重叠、同一天目标顺序是否符合优先级、每个目标是否排够（排不够的写进 `unmet_goals`）。

> 这 6 条不放进 Pydantic 的原因：AI 交出错数据是**常态**而不是意外。我们想把它攒成清单告诉用户「这份计划哪里不对」，而不是让接口直接炸一个 422 回去。

## 第一版功能范围

**必须完成：**

1. 添加多个学习目标，设置总学习时长、截止日期和优先级。
2. 设置计划日期范围、每天可用时间段和每日学习时长上限。
3. 请求 AI 根据以上条件生成结构化计划。
4. 校验 AI 返回的格式和基本时间约束。
5. 按日期展示计划，并显示每个学习时段对应的目标和时长。
6. 保存目标、用户设置和生成的计划。
7. 用户修改条件后，可以重新生成计划。

**后续加入：**

1. 标记学习时段已完成、部分完成或延期。
2. 记录实际学习时长。
3. AI 根据执行情况和剩余目标重新安排未完成部分。
4. 展示重排前后的变化及调整理由。

## 第一版暂不包含

- 由程序实现复杂的自动排程或优化算法。
- 多 Agent 协作、机器学习效率预测。
- 手机 App、多人协作和复杂日历平台接入。
- 用统一的"最佳作息"替代用户自己的作息偏好。

## 建议使用的核心数据

- **每个学习目标**至少包含：名称、总目标时长、截止日期、优先级。
- **用户时间设置**至少包含：计划开始和结束日期、每天可学习时间段、每日学习时长上限、休息偏好。
- **AI 返回的每个学习时段**至少包含：日期、目标名称、开始时间、结束时间、学习时长和安排理由。若目标无法按条件完成，还要返回未完成时长和原因。

已落地为 `app/models.py` 里的六个模型（字段形状以 `samples/sample_plan.json` 为准，改代码记得同步改样例）：

| 模型 | 层 | 字段 |
| --- | --- | --- |
| `GoalInput` | 单个目标 | `title` / `total_minutes` / `deadline` / `priority` |
| `PlanRequest` | 请求 | `start_date` / `end_date` / `available_start` / `available_end` / `daily_limit_minutes` / `break_minutes` / `study_order` / `goals` |
| `StudyBlock` | 一个时段 | `goal_title` / `start_time` / `end_time` / `minutes` / `reason` |
| `DayPlan` | 一天 | `plan_date` / `total_minutes` / `blocks` |
| `UnmetGoal` | 排不完的目标 | `goal_title` / `remaining_minutes` / `reason` |
| `PlanResponse` | 响应 | `daily_plans` / `unmet_goals` |

> 范围上先做"输入多个目标 → AI 生成计划 → 校验 → 前端展示"，再加入执行反馈和动态重排。

## 环境要求

| 组件 | 已装版本 | 说明 |
| --- | --- | --- |
| Python | 3.12.10（64 位） | 用 `py -3.12` 调用 |
| VS Code | 1.136.2 | 含 Microsoft Python 扩展 + Pylance |
| Git | 2.55.0 | 用户已配置为 `xxzg` / `xyh_06@qq.com` |

## 本机命令（Windows PowerShell 为准）

```powershell
# 进入项目
cd C:\Users\xyh_0\dev\adaptive-task-planner-agent

# 直接调用虚拟环境里的 Python（不依赖 PowerShell 脚本执行策略）
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install "fastapi[standard]"
.\.venv\Scripts\python.exe -m pip freeze > requirements.txt

# 启动服务：浏览器打开 http://127.0.0.1:8000/docs 看自动生成的接口文档
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

> 为什么用 `.\.venv\Scripts\python.exe` 而不是先 `activate`：
> PowerShell 默认禁止运行脚本（ExecutionPolicy 为 Restricted），
> 直接写全路径可以完全绕开激活步骤，不会踩到这个坑。

## 访问 GitHub（2026-10-19 实测更新）

**本机直连 GitHub 可用，不需要任何代理。** 实测数据：

| 测试项 | 结果 |
| --- | --- |
| `curl https://github.com` | HTTP 200，耗时 2.26s |
| `git clone` 公开仓库 | 成功 |
| `git ls-remote` 自己的仓库 | 成功（HEAD = `67085d9d`） |

之前推不动的真正原因：gitignore 全局配置写死了 `http.proxy = 127.0.0.1:7890`（曾经的 Clash 端口），
而 Clash 已经停用 → 每次连接都卡在 `"Failed to connect to github.com:443 over proxy 127.0.0.1"`。
**该代理配置已于 2026-10-19 清除**，现在 `git push` / `clone` 直接走直连。

> 以后如果又遇到同类报错，用这条判断：
> ```powershell
> git ls-remote --heads origin
> ```
> 秒回就是网络没问题；报 `over proxy 127.0.0.1` 说明又被代理劫持了，临时绕开的办法是
> `git -c http.proxy= -c https.proxy= <命令>`。

将来若某天觉得速度慢想重新挂 Clash：

```powershell
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
# 恢复直连：
git config --global --unset http.proxy
git config --global --unset https.proxy
```

## 首次推送

在 GitHub 网页上新建空仓库 `adaptive-task-planner-agent`（不要勾 README），然后：

```powershell
git init
git add .
git commit -m "init: 项目骨架与 FastAPI 最小示例"
git branch -M main
git remote add origin https://github.com/你的用户名/adaptive-task-planner-agent.git
git push -u origin main
```

登录提示会由 Git Credential Manager 弹出，用 GitHub 账号登录即可（不要用账号密码）。

## 当前已实现的接口

服务启动后打开 <http://127.0.0.1:8000/docs> 可看到自动生成的接口文档，并能直接在线调试。
下面这些是"收集条件、保存、展示"这一层已经跑通的部分，AI 生成与校验接口按上面的第一版范围继续加。

| 方法 | 路径 | 作用 |
| --- | --- | --- |
| GET | `/health` | 健康检查 |
| POST | `/tasks` | 新增任务，成功返回 201 |
| GET | `/tasks` | 任务列表 |
| PUT | `/settings/day` | 保存或覆盖某一天的作息设置（同一天重复保存是覆盖，不是新增） |
| GET | `/settings/day?target_date=2026-10-23` | 查询某一天的作息设置 |
| POST | `/events` | 新增固定事件，成功返回 201 |
| GET | `/events?target_date=2026-10-23` | 查询某一天的固定事件，按开始时间排序 |

状态码约定：

- **422** 字段格式不对（日期写成"周三"、时长超出范围、必填参数没传），由 Pydantic 自动返回
- **400** 业务规则不满足（结束时间早于开始、事件落在可用窗口之外），由接口手动返回
- **404** 指定日期查不到数据

## 数据表

| 表 | 主键 | 说明 |
| --- | --- | --- |
| `tasks` | `id` | 任务 |
| `day_settings` | `target_date` | 一天的作息设置，一天只有一行 |
| `fixed_events` | `id` | 固定事件，一天可以有多行 |

日期与时间统一以 ISO 格式字符串存储（如 `2026-10-23`、`09:00:00`）。这样字典序恰好等于时间序，可以直接在 SQL 里比大小和排序。

后续按第一版范围还需要加的表：学习目标（`goals`，含总时长、截止日期、优先级）、计划日期范围与每日上限（`plan_settings`）、AI 生成的学习时段（`plan_blocks`，含安排理由、未完成时长与原因）以及执行反馈（`block_status`）。

## 数据

任务数据保存在 data/planner.db（SQLite，本地文件，不提交到 Git）。
服务启动时会自动建表，无需手动初始化。

> `app/scheduler.py` 里目前放着一段程序排期的占位实现。按"第一版暂不包含"的约定，复杂的自动排程与优化算法不作为主线，排期交给 AI，程序只负责校验与展示。
