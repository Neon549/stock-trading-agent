---
title: A股 Trading Agent System
sdk: docker
app_port: 7860
---

# A股 Trading Agent System

基于 LangGraph Multi-Agent + RAG 的 A股智能分析系统。

## 项目简介

这是一个面向 A股场景的智能交易分析系统，核心能力包括：

- 基本面分析
- 技术面分析
- 情绪分析
- 多智能体协作决策
- 历史决策记忆
- RAG 新闻检索

系统后端基于 FastAPI，工作流编排基于 LangGraph，支持后续部署到 Hugging Face Spaces。

## 项目结构

```text
.
├── agents/
├── api/
├── config/
├── evaluation/
├── graph/
├── memory/
├── rag/
├── tools/
├── main.py
├── requirements.txt
├── README.md
└── Dockerfile