
import os
import pickle
from datetime import datetime
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import akshare as ak

# ============================================================
# 为什么用 HuggingFaceEmbeddings 而不是 OpenAI Embeddings？
# 1. 免费，不消耗 API token
# 2. 本地运行，速度快
# 3. 用中文模型效果更好
# 对应知识库 4.x RAG 基础
# ============================================================

# 中文向量模型，首次运行会自动下载（约400MB）
EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"
FAISS_INDEX_PATH = "rag/faiss_index"


# def get_embeddings():
#     """获取向量化模型"""
#     return HuggingFaceEmbeddings(
#         model_name=EMBEDDING_MODEL,
#         model_kwargs={"device": "cpu"},
#         encode_kwargs={"normalize_embeddings": True},
#     )
# 全局单例，服务启动时加载一次，之后复用
import threading

_embeddings = None
_embeddings_lock = threading.Lock()

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        with _embeddings_lock:
            if _embeddings is None:  # 双重检查
                print("🔢 首次加载向量模型...")
                _embeddings = HuggingFaceEmbeddings(
                    model_name=EMBEDDING_MODEL,
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True},
                )
                print("✅ 向量模型加载完成，后续复用")
    return _embeddings

def fetch_news(stock_code: str) -> list[dict]:
    """
    从 akshare 抓取股票新闻
    返回格式：[{"title": ..., "content": ..., "date": ...}]
    """
    news_list = []
    try:
        df = ak.stock_news_em(symbol=stock_code)
        for _, row in df.iterrows():
            news_list.append({
                "title": row.get("新闻标题", ""),
                "content": row.get("新闻内容", row.get("新闻标题", "")),
                "date": str(row.get("发布时间", "")),
                "source": "东方财富",
            })
        print(f"✅ 抓取到 {len(news_list)} 条新闻")
    except Exception as e:
        print(f"❌ 抓取新闻失败: {e}")
    return news_list


def build_index(stock_code: str) -> FAISS:
    """
    构建向量索引

    流程：
    1. 抓取新闻
    2. 文本切块（Chunking）
    3. 向量化（Embedding）
    4. 存入 FAISS
    """
    print(f"🔨 开始为 {stock_code} 构建 RAG 索引...")

    # Step 1: 抓取新闻
    news_list = fetch_news(stock_code)
    if not news_list:
        # 没有新闻时用占位文本，避免空索引报错
        news_list = [{"title": "暂无新闻", "content": f"{stock_code}暂无相关新闻", "date": "", "source": ""}]

    # Step 2: 准备文本和元数据
    texts = []
    metadatas = []
    for news in news_list:
        # 把标题和内容合并，标题权重更高（重复一次）
        full_text = f"{news['title']}\n{news['title']}\n{news['content']}"
        texts.append(full_text)
        metadatas.append({
            "title": news["title"],
            "date": news["date"],
            "source": news["source"],
            "stock_code": stock_code,
        })

    # Step 3: 文本切块
    # ============================================================
    # 为什么要切块？
    # chunk_size=500：每块最多500个字符
    # chunk_overlap=50：相邻块重叠50字，避免关键信息被切断
    # 对应知识库 4.2 中的 chunking 策略
    # ============================================================
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "，", " "],
    )

    split_texts = []
    split_metadatas = []
    for text, metadata in zip(texts, metadatas):
        chunks = splitter.split_text(text)
        split_texts.extend(chunks)
        split_metadatas.extend([metadata] * len(chunks))

    print(f"📄 切块完成：{len(texts)} 篇新闻 → {len(split_texts)} 个文本块")

    # Step 4: 向量化 + 存入 FAISS
    print("🔢 正在向量化（首次运行需下载模型）...")
    embeddings = get_embeddings()

    vectorstore = FAISS.from_texts(
        texts=split_texts,
        embedding=embeddings,
        metadatas=split_metadatas,
    )

    # 持久化保存索引
    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    index_file = f"{FAISS_INDEX_PATH}/{stock_code}"
    vectorstore.save_local(index_file)
    print(f"💾 索引已保存到 {index_file}")

    return vectorstore


def load_index(stock_code: str) -> FAISS | None:
    """加载已有索引，不存在则返回 None"""
    index_file = f"{FAISS_INDEX_PATH}/{stock_code}"
    if not os.path.exists(index_file):
        return None
    embeddings = get_embeddings()
    return FAISS.load_local(
        index_file,
        embeddings,
        allow_dangerous_deserialization=True,
    )


def get_or_build_index(stock_code: str) -> FAISS:
    vectorstore = load_index(stock_code)
    if vectorstore is None:
        vectorstore = build_index(stock_code)
    return vectorstore