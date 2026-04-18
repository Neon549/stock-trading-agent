#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: yulin
@created: 2026/4/17 17:19
@updated: 2026/4/17 17:19
@version: 1.0
@description: 
"""

from akshare_tools import get_stock_price, get_stock_history

# 测试获取平安银行实时行情
print(get_stock_price.invoke({"symbol": "000001"}))
print("---")
# 测试获取历史K线
print(get_stock_history.invoke({"symbol": "000001", "days": 10}))