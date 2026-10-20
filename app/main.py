#此文件时用来定义URL和HTTP方法，收强求、调校验、调算法，把结果转成json返回

#导入一个类，这个类可以帮我写http接口,可以帮我建立url，检查字段合法，自动生成Swagger文档页
from fastapi import FastAPI

#造一个应用对象，名字叫app，是一个空的路由表
app = FastAPI(title="自适应任务规划助手") #**

#注册，建立url。并在表里加一行GET /health
@app.get("/health")
#函数负责GET /health
def health_check():
    return {"status": "ok"} #返回一个字典，FastAPI自动转成JSON





























