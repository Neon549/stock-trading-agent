#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: yulin
@created: 2026/4/18 22:59
@updated: 2026/4/18 22:59
@version: 1.0
@description: 
"""

# app.py

import streamlit as st
import requests
import json
import time

# ============================================================
# Streamlit 基本概念：
# 每次用户操作（点击按钮、输入文字）页面会整体重新运行
# st.session_state 用来保存跨次运行的数据
# 对应知识库 9.x 系统架构设计
# ============================================================

API_BASE = "http://localhost:8000/api/v1"

# 页面配置
st.set_page_config(
    page_title="A股智能交易分析系统",
    page_icon="📈",
    layout="wide",
)

# 初始化 session state
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "is_analyzing" not in st.session_state:
    st.session_state.is_analyzing = False

# ---- 页面标题 ----
st.title("📈 A股智能交易分析系统")
st.caption("基于 LangGraph Multi-Agent + RAG 的智能分析平台")

st.divider()

# ---- 左侧输入区 ----
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🔍 分析设置")

    stock_code = st.text_input(
        "股票代码",
        value="600487",
        placeholder="如: 600487",
        help="输入6位A股股票代码"
    )

    # 快捷股票按钮
    st.caption("快捷选择：")
    quick_cols = st.columns(3)
    if quick_cols[0].button("亨通光电\n600487"):
        stock_code = "600487"
    if quick_cols[1].button("贵州茅台\n600519"):
        stock_code = "600519"
    if quick_cols[2].button("宁德时代\n300750"):
        stock_code = "300750"

    st.divider()

    # 检查后端是否在线
    try:
        r = requests.get(f"{API_BASE}/health", timeout=2)
        if r.status_code == 200:
            st.success("✅ 后端服务正常")
        else:
            st.error("❌ 后端服务异常")
    except:
        st.error("❌ 后端未启动，请先运行 python main.py")

    analyze_btn = st.button(
        "🚀 开始分析",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.is_analyzing,
    )

    # 查看历史按钮
    history_btn = st.button(
        "📋 查看历史决策",
        use_container_width=True,
    )

# ---- 右侧结果区 ----
with col2:
    # 触发分析
    if analyze_btn and stock_code:
        st.session_state.is_analyzing = True
        st.session_state.analysis_result = None

        # 显示进度
        progress_container = st.container()
        with progress_container:
            st.subheader(f"正在分析 {stock_code}...")

            steps = [
                ("📊 基本面分析师", "读取财务数据..."),
                ("📈 技术面分析师", "分析K线走势..."),
                ("📰 情绪分析师", "检索新闻资讯..."),
                ("🔬 研究员", "多空辩论中..."),
                ("💼 交易员", "生成交易决策..."),
            ]

            progress_bar = st.progress(0)
            status_text = st.empty()

            # 显示步骤动画
            for i, (agent, action) in enumerate(steps):
                status_text.markdown(f"**{agent}** — {action}")
                progress_bar.progress((i + 1) / len(steps) * 0.8)
                time.sleep(0.5)

            status_text.markdown("**⏳ 等待 AI 分析完成...**")

            try:
                # 调用后端 API
                response = requests.post(
                    f"{API_BASE}/analyze",
                    json={"stock_code": stock_code},
                    timeout=300,
                )

                if response.status_code == 200:
                    result = response.json()
                    st.session_state.analysis_result = result
                    progress_bar.progress(1.0)
                    status_text.markdown("**✅ 分析完成！**")
                else:
                    st.error(f"分析失败：{response.json().get('detail', '未知错误')}")

            except requests.exceptions.Timeout:
                st.error("请求超时，分析时间过长，请重试")
            except Exception as e:
                st.error(f"请求失败：{str(e)}")

            st.session_state.is_analyzing = False

    # 显示分析结果
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        decision_text = result.get("decision", "")

        # 决策颜色
        if "买入" in decision_text:
            decision_color = "🟢"
            box_color = "success"
        elif "卖出" in decision_text or "减仓" in decision_text:
            decision_color = "🔴"
            box_color = "error"
        else:
            decision_color = "🟡"
            box_color = "warning"

        # 决策摘要卡片
        st.subheader(f"{decision_color} 交易决策 — {result['stock_code']}")

        # 用 tabs 展示各部分
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "💼 最终决策",
            "📊 基本面",
            "📈 技术面",
            "📰 情绪分析",
            "🔬 研究员辩论",
        ])

        with tab1:
            st.markdown(decision_text)

        with tab2:
            st.markdown(result.get("fundamental_report", "暂无"))

        with tab3:
            st.markdown(result.get("technical_report", "暂无"))

        with tab4:
            st.markdown(result.get("sentiment_report", "暂无"))

        with tab5:
            st.markdown(result.get("researcher_analysis", "暂无"))

    # 显示历史记录
    if history_btn and stock_code:
        try:
            r = requests.get(f"{API_BASE}/history/{stock_code}", timeout=10)
            if r.status_code == 200:
                history = r.json().get("history", "")
                st.subheader(f"📋 {stock_code} 历史决策")
                st.markdown(history)
        except Exception as e:
            st.error(f"获取历史失败：{str(e)}")

    # 默认提示
    if not st.session_state.analysis_result and not history_btn:
        st.info("👈 输入股票代码，点击「开始分析」按钮启动 Multi-Agent 分析")

        st.markdown("""
        ### 系统架构
        输入股票代码
         ↓
    📊 基本面分析师 ── 财务数据 + yfinance
         ↓
    📈 技术面分析师 ── K线数据 + 技术指标
         ↓  
    📰 情绪分析师   ── RAG检索 + 新闻分析
         ↓
    🔬 研究员       ── 多空辩论
         ↓
    💼 交易员       ── 最终决策 + 存入Memory"""
            )