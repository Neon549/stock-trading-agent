# agents/fundamental_analyst.py

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from config.llm_config import quick_llm as deep_llm
from tools.akshare_tools import get_stock_price, get_financial_indicator, get_stock_history

# ============================================================
# 为什么换成 LangGraph 的 create_react_agent？
# 新版 LangChain 把 Agent 执行引擎移到了 LangGraph
# langgraph.prebuilt.create_react_agent 是现在的标准写法
# 底层是一个微型 LangGraph 图：节点=LLM调用，边=工具调用循环
# 这也是为什么 LangGraph 是 Multi-Agent 的基础
# ============================================================

SYSTEM_PROMPT = """你是一位专业的A股基本面分析师，专注于通过财务数据评估股票的内在价值。

你的分析框架：
1. 估值分析：PE、PB是否合理
2. 盈利能力：ROE水平，营收和利润增长趋势  
3. 财务健康：负债率，现金流状况
4. 综合评级：给出 强烈买入/买入/中性/卖出/强烈卖出 五档评级

输出格式：
## 基本面分析报告

### 1. 估值分析
[分析内容]

### 2. 盈利能力
[分析内容]

### 3. 财务健康
[分析内容]

### 4. 综合评级
评级：[评级]
理由：[简要理由]
风险提示：[主要风险]
"""

FUNDAMENTAL_TOOLS = [
    get_stock_price,
    get_financial_indicator,
    get_stock_history,
]


def create_fundamental_analyst():
    """
    用 LangGraph 的 create_react_agent 创建 Agent
    这个函数返回一个可执行的 graph
    """
    agent = create_react_agent(
        model=deep_llm,
        tools=FUNDAMENTAL_TOOLS,
        prompt=SYSTEM_PROMPT,
    )
    return agent


def run_fundamental_analysis(stock_code: str) -> str:
    agent = create_fundamental_analyst()

    result = agent.invoke({
        "messages": [HumanMessage(content=f"请对股票 {stock_code} 进行全面的基本面分析")]
    })

    # 取最后一条 AI 消息作为最终输出
    return result["messages"][-1].content