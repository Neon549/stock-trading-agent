# memory/short_term.py

import sqlite3
import json
from datetime import datetime
from pathlib import Path

# ============================================================
# 长期记忆：对应知识库 8.3
# 用 SQLite 存储历史决策
# 为什么用 SQLite 而不是 Redis？
# - SQLite：文件型数据库，零配置，适合单机部署
# - Redis：内存数据库，适合分布式/高并发场景
# 我们是单机项目，SQLite 完全够用
# ============================================================

DB_PATH = Path("memory/trading_memory.db")


def init_db():
    """初始化数据库，创建表结构"""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS trading_decisions
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       stock_code
                       TEXT
                       NOT
                       NULL,
                       analysis_date
                       TEXT
                       NOT
                       NULL,
                       decision
                       TEXT
                       NOT
                       NULL,
                       fundamental_summary
                       TEXT,
                       technical_summary
                       TEXT,
                       sentiment_summary
                       TEXT,
                       target_price
                       REAL,
                       stop_loss
                       REAL,
                       actual_result
                       TEXT,
                       created_at
                       TEXT
                       NOT
                       NULL
                   )
                   """)

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS analysis_reflections
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       stock_code
                       TEXT
                       NOT
                       NULL,
                       reflection
                       TEXT
                       NOT
                       NULL,
                       created_at
                       TEXT
                       NOT
                       NULL
                   )
                   """)

    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")


class LongTermMemory:
    """
    长期记忆管理器
    负责存储和检索历史交易决策
    """

    def __init__(self):
        init_db()

    def save_decision(
            self,
            stock_code: str,
            decision: str,
            fundamental_summary: str = "",
            technical_summary: str = "",
            sentiment_summary: str = "",
    ):
        """保存一次分析决策"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
                       INSERT INTO trading_decisions
                       (stock_code, analysis_date, decision, fundamental_summary,
                        technical_summary, sentiment_summary, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)
                       """, (
                           stock_code,
                           datetime.now().strftime("%Y-%m-%d"),
                           decision[:500],  # 截断避免太长
                           fundamental_summary[:300],
                           technical_summary[:300],
                           sentiment_summary[:300],
                           datetime.now().isoformat(),
                       ))

        conn.commit()
        conn.close()
        print(f"💾 决策已保存到长期记忆")

    def get_history(self, stock_code: str, limit: int = 3) -> str:
        """
        获取某只股票的历史决策
        返回格式化字符串，方便塞进 prompt
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT analysis_date, decision, created_at
                       FROM trading_decisions
                       WHERE stock_code = ?
                       ORDER BY created_at DESC LIMIT ?
                       """, (stock_code, limit))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"暂无 {stock_code} 的历史分析记录"

        history = [f"## {stock_code} 历史决策记录"]
        for date, decision, created_at in rows:
            history.append(f"\n### {date}\n{decision[:200]}...")

        return "\n".join(history)

    def save_reflection(self, stock_code: str, reflection: str):
        """保存复盘反思（对应知识库 8.3 长期记忆的自我改进）"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
                       INSERT INTO analysis_reflections (stock_code, reflection, created_at)
                       VALUES (?, ?, ?)
                       """, (stock_code, reflection, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_reflections(self, stock_code: str) -> str:
        """获取历史复盘"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT reflection, created_at
                       FROM analysis_reflections
                       WHERE stock_code = ?
                       ORDER BY created_at DESC LIMIT 3
                       """, (stock_code,))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "暂无复盘记录"

        return "\n\n".join([f"[{r[1][:10]}] {r[0]}" for r in rows])
