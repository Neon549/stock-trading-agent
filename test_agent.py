#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: yulin
@created: 2026/4/17 17:25
@updated: 2026/4/17 17:25
@version: 1.0
@description:
"""

# test_agent.py
from agents.fundamental_analyst import run_fundamental_analysis
from agents.technical_analyst import run_technical_analysis

# 注释掉基本面，先测技术面（快一点）
# result = run_fundamental_analysis("600487")
# result = run_technical_analysis("000988")
# 先单独测试工具是否正常
from tools.akshare_tools import get_stock_price, get_stock_history

# print("=== 测试工具 ===")
# print(get_stock_price.invoke({"symbol": "000988"}))
# print("\n")
# print(get_stock_history.invoke({"symbol": "000988", "days": 30}))
#
# print("\n=== 测试 Agent ===")
# result = run_technical_analysis("000988")
#print(result)
# test_agent.py
from graph.trading_graph import run_trading_analysis

print("🚀 启动 Multi-Agent 交易分析系统")
print("=" * 50)

result = run_trading_analysis("600487")

print("\n" + "=" * 50)
print("📋 最终交易决策：")
print(result["final_decision"])