# api/routes.py

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from graph.trading_graph import run_trading_analysis
from memory.long_term import LongTermMemory

router = APIRouter()
memory = LongTermMemory()


# ============================================================
# Pydantic 模型：定义请求和响应的数据结构
# 对应知识库 9.x 系统架构设计
# FastAPI 自动做数据验证，类型不对直接报错
# ============================================================

class AnalyzeRequest(BaseModel):
    stock_code: str
    force_refresh: bool = False  # 是否强制刷新 RAG 索引


class AnalyzeResponse(BaseModel):
    stock_code: str
    decision: str
    fundamental_report: str
    technical_report: str
    sentiment_report: str
    researcher_analysis: str
    status: str = "success"


class HistoryResponse(BaseModel):
    stock_code: str
    history: str


@router.get("/health")
def health_check():
    """健康检查接口，确认服务是否正常运行"""
    return {"status": "ok", "message": "Trading Agent System is running"}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_stock(request: AnalyzeRequest):
    """
    核心接口：对股票进行完整的 Multi-Agent 分析

    对应知识库 9.1 Agent 系统架构
    这个接口会依次调用：
    基本面分析师 → 技术面分析师 → 情绪分析师 → 研究员 → 交易员
    """
    try:
        stock_code = request.stock_code.strip()

        if not stock_code:
            raise HTTPException(status_code=400, detail="股票代码不能为空")

        print(f"📨 收到分析请求：{stock_code}")
        result = run_trading_analysis(stock_code)

        return AnalyzeResponse(
            stock_code=stock_code,
            decision=result.get("final_decision", ""),
            fundamental_report=result.get("fundamental_report", ""),
            technical_report=result.get("technical_report", ""),
            sentiment_report=result.get("sentiment_report", ""),
            researcher_analysis=result.get("bull_argument", ""),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败：{str(e)}")


@router.get("/history/{stock_code}", response_model=HistoryResponse)
def get_history(stock_code: str):
    """获取某只股票的历史决策记录"""
    history = memory.get_history(stock_code)
    return HistoryResponse(stock_code=stock_code, history=history)


@router.get("/stocks/info/{stock_code}")
def get_stock_info(stock_code: str):
    """快速获取股票基本信息，不触发完整分析"""
    try:
        from tools.akshare_tools import get_stock_price
        result = get_stock_price.invoke({"symbol": stock_code})
        return {"stock_code": stock_code, "info": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))