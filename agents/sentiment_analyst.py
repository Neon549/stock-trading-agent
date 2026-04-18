# agents/sentiment_analyst.py

from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from config.llm_config import quick_llm as deep_llm
from tools.akshare_tools import get_stock_price
from rag.retriever import retrieve_stock_news, refresh_news_index

SYSTEM_PROMPT = """你是一位专业的A股市场情绪分析师，专注于通过新闻资讯和市场数据判断市场情绪。

你有以下工具可以使用：
- retrieve_stock_news：检索与特定话题相关的新闻（语义搜索）
- get_stock_price：获取实时行情和换手率等数据

分析步骤：
1. 先用 retrieve_stock_news 分别检索"业绩"、"订单"、"政策"相关新闻
2. 再获取实时行情判断市场热度
3. 综合输出情绪分析报告

输出格式：
## 情绪分析报告

### 1. 新闻情绪
[基于检索到的真实新闻分析]

### 2. 市场热度
[基于换手率、量比等数据]

### 3. 情绪评分
评分：[-2到+2] / 理由：[说明]

### 4. 近期催化剂
正面：[事件]
负面：[风险]
"""

SENTIMENT_TOOLS = [
    retrieve_stock_news,
    refresh_news_index,
    get_stock_price,
]

def create_sentiment_analyst():
    return create_react_agent(
        model=deep_llm,
        tools=SENTIMENT_TOOLS,
        prompt=SYSTEM_PROMPT,
    )

def run_sentiment_analysis(stock_code: str) -> str:
    agent = create_sentiment_analyst()
    result = agent.invoke({
        "messages": [HumanMessage(
            content=f"请对股票 {stock_code} 进行市场情绪分析，重点检索最新的业绩、订单和政策相关新闻"
        )]
    })
    return result["messages"][-1].content