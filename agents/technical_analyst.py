# agents/technical_analyst.py

from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from config.llm_config import quick_llm as deep_llm
from tools.akshare_tools import get_stock_price, get_stock_history

# ============================================================
# 技术面分析师 vs 基本面分析师的区别：
# 1. system prompt 完全不同——关注K线形态、技术指标
# 2. 用的 tools 不同——不需要财务指标，只需要历史K线
# 3. 分析逻辑不同——短期价格行为而非内在价值
# 这体现了 Multi-Agent 的核心思想：
# 每个 Agent 职责单一，各自做最擅长的事
# ============================================================

SYSTEM_PROMPT = """你是一位专业的A股技术面分析师，专注于通过价格和成交量数据判断股票的短中期走势。

你的分析框架：
1. 趋势分析：当前处于上升/下降/盘整趋势，关键均线支撑压力位
2. 量价关系：成交量是否配合价格运动，量价背离信号
3. 关键价位：近期支撑位、压力位、突破点
4. 短期展望：未来1-2周的价格走势预判

输出格式：
## 技术面分析报告

### 1. 趋势分析
[分析内容]

### 2. 量价关系
[分析内容]

### 3. 关键价位
支撑位：[价格]
压力位：[价格]

### 4. 短期展望
方向：[看多/看空/中性]
目标价：[价格区间]
止损位：[价格]
"""

TECHNICAL_TOOLS = [
    get_stock_price,
    get_stock_history,
]

def create_technical_analyst():
    return create_react_agent(
        model=deep_llm,
        tools=TECHNICAL_TOOLS,
        prompt=SYSTEM_PROMPT,
    )

def run_technical_analysis(stock_code: str) -> str:
    agent = create_technical_analyst()
    result = agent.invoke({
        "messages": [HumanMessage(content=f"请对股票 {stock_code} 进行技术面分析，获取最近30天K线数据")]
    })
    return result["messages"][-1].content