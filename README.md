# Adaptive Task Planner Agent

自适应任务排期 Agent：用 FastAPI 提供接口，根据任务剩余量与每日可用时长动态生成计划。

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

## 推 GitHub 前必读：Clash 代理

本机 git 全局配置了 `http.proxy` / `https.proxy` 指向 `127.0.0.1:7890`（Clash）。
**Clash 没运行时，所有 clone / push / pull 会直接失败**，报错形如
`Failed to connect to github.com:443 over proxy 127.0.0.1`。

处理方式二选一：

```powershell
# 方式一：开着 Clash 再操作（推荐，直连国内常不通）
git push

# 方式二：临时绕过代理单次操作
git -c http.proxy= -c https.proxy= push
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
