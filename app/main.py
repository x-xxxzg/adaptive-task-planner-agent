"""FastAPI 应用入口。

本文件只保留最小可运行骨架，用来验证环境是否正常。
后续按教程把真正的接口写在这里。
"""

from fastapi import FastAPI

app = FastAPI(title="Adaptive Task Planner Agent")


@app.get("/")
def index() -> dict[str, str]:
    """根路径：返回一条问候，用来确认服务已启动。"""
    return {"message": "Adaptive Task Planner Agent 已启动"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
