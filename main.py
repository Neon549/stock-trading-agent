# main.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

# ============================================================
# FastAPI 应用初始化
# CORSMiddleware：允许跨域请求
# 前端（Streamlit/React）和后端不在同一个端口
# 必须加这个中间件，否则浏览器会拦截请求
# ============================================================

app = FastAPI(
    title="A股 Trading Agent System",
    description="基于 LangGraph Multi-Agent 的A股智能分析系统",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "A股 Trading Agent System",
        "docs": "/docs",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )