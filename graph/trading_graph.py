# graph/trading_graph.py

from langgraph.graph import StateGraph, END
from langgraph.types import Send
from langchain_core.messages import HumanMessage
from graph.state import TradingState
from agents.fundamental_analyst import run_fundamental_analysis
from agents.technical_analyst import run_technical_analysis
from agents.sentiment_analyst import run_sentiment_analysis
from config.llm_config import deep_llm
from memory.long_term import LongTermMemory
import concurrent.futures

memory = LongTermMemory()

# ============================================================
# 并行执行的核心思路（对应知识库 12.1 并发Agent系统设计）：
# 用 Python 的 ThreadPoolExecutor 同时跑三个分析师
# 三个都完成后再继续研究员节点
# 比 LangGraph Send API 更直观，适合我们的场景
# ============================================================

def analysts_node(state: TradingState) -> dict:
    """
    并行分析节点：同时运行三个分析师
    用 ThreadPoolExecutor 实现真正的并行
    """
    stock_code = state["stock_code"]
    print(f"\n🚀 三个分析师并行启动：{stock_code}")

    def run_fundamental():
        print("📊 [基本面分析师] 开始...")
        result = run_fundamental_analysis(stock_code)
        print("✅ 基本面分析完成")
        return result

    def run_technical():
        print("📈 [技术面分析师] 开始...")
        result = run_technical_analysis(stock_code)
        print("✅ 技术面分析完成")
        return result

    def run_sentiment():
        print("📰 [情绪分析师] 开始...")
        result = run_sentiment_analysis(stock_code)
        print("✅ 情绪分析完成")
        return result

    # 三个线程同时跑
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_fundamental = executor.submit(run_fundamental)
        future_technical = executor.submit(run_technical)
        future_sentiment = executor.submit(run_sentiment)

        fundamental_report = future_fundamental.result()
        technical_report = future_technical.result()
        sentiment_report = future_sentiment.result()

    print("\n✅ 三个分析师全部完成，进入研究员节点")

    return {
        "fundamental_report": fundamental_report,
        "technical_report": technical_report,
        "sentiment_report": sentiment_report,
    }


def researcher_node(state: TradingState) -> dict:
    """研究员节点：综合三份报告，进行多空辩论"""
    print(f"\n🔬 [研究员] 综合分析，进行多空辩论...")

    prompt = f"""你是一位资深A股研究员，需要基于以下三份分析报告进行多空辩论。

## 基本面分析报告
{state['fundamental_report']}

## 技术面分析报告
{state['technical_report']}

## 情绪分析报告
{state['sentiment_report']}

请分别给出：
### 多方观点（看涨理由）
[从三份报告中提炼支持买入的核心论据，3-5条]

### 空方观点（看跌理由）
[从三份报告中提炼支持卖出/观望的核心论据，3-5条]

### 综合倾向
[多方占优/空方占优/势均力敌] - [简要理由]
"""

    response = deep_llm.invoke([HumanMessage(content=prompt)])
    result = response.content
    print("✅ 多空辩论完成")
    return {
        "bull_argument": result,
        "debate_rounds": state.get("debate_rounds", 0) + 1,
    }


def trader_node(state: TradingState) -> dict:
    """交易员节点：做出最终决策"""
    print(f"\n💼 [交易员] 综合所有信息，做出最终决策...")

    history = memory.get_history(state["stock_code"])

    prompt = f"""你是一位经验丰富的A股交易员，需要基于研究团队的分析做出最终交易决策。

## 历史决策记录（避免重复犯错）
{history}

## 研究员综合分析
{state['bull_argument']}

## 决策要求
请给出明确的交易指令：

### 交易决策
决策：[强烈买入 / 买入 / 持有观望 / 减仓 / 卖出]
建议仓位：[如：总资金的20%]
建议买入价位：[价格区间或条件]
目标价：[价格]
止损价：[价格]
持有周期：[短线1-2周 / 中线1-3月]

### 决策依据
[3条核心理由]

### 风险提示
[2-3条主要风险]
"""

    response = deep_llm.invoke([HumanMessage(content=prompt)])
    decision = response.content

    memory.save_decision(
        stock_code=state["stock_code"],
        decision=decision,
        fundamental_summary=state.get("fundamental_report", "")[:300],
        technical_summary=state.get("technical_report", "")[:300],
        sentiment_summary=state.get("sentiment_report", "")[:300],
    )

    print("✅ 交易决策完成并已存入记忆")
    return {"final_decision": decision}


def build_trading_graph():
    """
    构建优化后的 Multi-Agent 工作流图

    优化前：基本面 → 技术面 → 情绪 → 研究员 → 交易员
    优化后：[基本面 + 技术面 + 情绪]并行 → 研究员 → 交易员
    """
    graph = StateGraph(TradingState)

    # 添加节点
    graph.add_node("analysts", analysts_node)      # 并行分析节点
    graph.add_node("researcher", researcher_node)
    graph.add_node("trader", trader_node)

    # 设置入口
    graph.set_entry_point("analysts")

    # 添加边
    graph.add_edge("analysts", "researcher")
    graph.add_edge("researcher", "trader")
    graph.add_edge("trader", END)

    return graph.compile()


trading_graph = build_trading_graph()


def run_trading_analysis(stock_code: str) -> dict:
    """对外接口"""
    initial_state = {
        "stock_code": stock_code,
        "fundamental_report": None,
        "technical_report": None,
        "sentiment_report": None,
        "bull_argument": None,
        "bear_argument": None,
        "debate_rounds": 0,
        "final_decision": None,
        "risk_assessment": None,
        "messages": [],
    }
    return trading_graph.invoke(initial_state)