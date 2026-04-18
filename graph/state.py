#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: yulin
@created: 2026/4/18 09:32
@updated: 2026/4/18 09:32
@version: 1.0
@description: 
"""

# graph/state.py
from typing import TypedDict, Optional
from langgraph.graph.message import add_messages
from typing import Annotated


# ============================================================
# State 是整个 Multi-Agent 系统的核心数据结构
# 对应知识库 10.3 Agent 通信——Agent 之间不直接对话
# 而是通过读写 State 来传递信息
# TypedDict 让每个字段都有明确类型，避免数据混乱
# ============================================================

class TradingState(TypedDict):
    # 输入
    stock_code: str  # 股票代码

    # 各 Agent 的分析结果
    fundamental_report: Optional[str]  # 基本面分析报告
    technical_report: Optional[str]  # 技术面分析报告
    sentiment_report: Optional[str]  # 情绪分析报告

    # 研究员辩论结果
    bull_argument: Optional[str]  # 多方论点
    bear_argument: Optional[str]  # 空方论点
    debate_rounds: int  # 已辩论轮数

    # 最终输出
    final_decision: Optional[str]  # 最终交易决策
    risk_assessment: Optional[str]  # 风险评估

    # 消息历史（对应知识库 8.2 短期记忆）
    messages: Annotated[list, add_messages]