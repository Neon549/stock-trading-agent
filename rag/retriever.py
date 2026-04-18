from langchain_core.tools import tool
from rag.indexer import get_or_build_index, build_index


@tool
def retrieve_stock_news(stock_code: str, query: str) -> str:
    """
    检索与股票相关的新闻资讯，基于语义相似度返回最相关的内容。
    stock_code: 股票代码，如 '600487'
    query: 检索关键词，如 '业绩增长' '海缆订单' '政策利好'
    """
    try:
        vectorstore = get_or_build_index(stock_code)
        docs = vectorstore.similarity_search(query, k=3)
        if not docs:
            return f"未找到与'{query}'相关的新闻"
        results = []
        for i, doc in enumerate(docs, 1):
            meta = doc.metadata
            results.append(
                f"【新闻{i}】{meta.get('date', '')} - {meta.get('title', '')}\n"
                f"{doc.page_content[:200]}..."
            )
        return f"检索到与'{query}'相关的新闻：\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"检索失败：{type(e).__name__}: {str(e)}"


@tool
def refresh_news_index(stock_code: str) -> str:
    """
    强制刷新股票新闻索引，获取最新资讯。
    stock_code: 股票代码，如 '600487'
    """
    try:
        build_index(stock_code)
        return f"✅ {stock_code} 新闻索引已更新"
    except Exception as e:
        return f"❌ 更新失败：{str(e)}"