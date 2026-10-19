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
