import akshare as ak  # 只用于 get_stock_news
import pandas as pd
import requests
import yfinance as yf
from langchain_core.tools import tool
from datetime import datetime, timedelta
from functools import lru_cache

# 设置全局 User-Agent，绕过 akshare 数据源的反爬限制
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})
ak.requests_session = session

@lru_cache(maxsize=128)
def _get_stock_history_cached(symbol: str, days: int, date_key: str):
    """使用 yfinance 获取历史数据，稳定不限流"""
    try:
        import yfinance as yf
        print(f"🔍 获取 {symbol} 历史数据...")

        # A股代码转换：6开头是上交所(.SS)，0/3开头是深交所(.SZ)
        if symbol.startswith('6'):
            yf_symbol = f"{symbol}.SS"
        else:
            yf_symbol = f"{symbol}.SZ"

        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period=f"{days}d")

        if df.empty:
            return pd.DataFrame()

        # 统一列名
        df = df.rename(columns={
            "Open": "开盘",
            "Close": "收盘",
            "High": "最高",
            "Low": "最低",
            "Volume": "成交量",
        })
        df.index = df.index.strftime("%Y-%m-%d")
        df.index.name = "日期"
        df = df.reset_index()

        print(f"✅ 成功获取 {len(df)} 条数据")
        return df

    except Exception as e:
        print(f"❌ 获取失败: {type(e).__name__}: {str(e)}")
        return pd.DataFrame()


@tool
def get_stock_price(symbol: str) -> str:
    """
    获取A股股票的实时行情数据。
    symbol: 股票代码，如 '600487'
    """
    try:
        import yfinance as yf
        yf_symbol = f"{symbol}.SS" if symbol.startswith('6') else f"{symbol}.SZ"
        ticker = yf.Ticker(yf_symbol)

        df = ticker.history(period="2d")
        if df.empty:
            return f"未找到股票代码 {symbol}"

        latest = df.iloc[-1]
        prev = df.iloc[-2]
        change_pct = (latest['Close'] - prev['Close']) / prev['Close'] * 100

        info = ticker.info

        return (
            f"股票：{info.get('longName', symbol)}（{symbol}）\n"
            f"最新价：{latest['Close']:.2f}\n"
            f"涨跌幅：{change_pct:.2f}%\n"
            f"成交量：{latest['Volume']:,.0f}\n"
            f"总市值：{info.get('marketCap', 'N/A')}\n"
            f"行业：{info.get('industry', 'N/A')}\n"
        )
    except Exception as e:
        return f"获取股价失败：{type(e).__name__}: {str(e)}"


@tool
def get_financial_indicator(symbol: str) -> str:
    """
    获取A股股票的核心财务指标，用于基本面分析。
    symbol: 股票代码，如 '600487'
    """
    try:
        import yfinance as yf
        yf_symbol = f"{symbol}.SS" if symbol.startswith('6') else f"{symbol}.SZ"
        ticker = yf.Ticker(yf_symbol)
        info = ticker.info

        return (
            f"股票：{info.get('longName', symbol)}（{symbol}）基本面指标\n"
            f"最新价：{info.get('currentPrice', 'N/A')}\n"
            f"市盈率(PE)：{info.get('trailingPE', 'N/A')}\n"
            f"市净率(PB)：{info.get('priceToBook', 'N/A')}\n"
            f"总市值：{info.get('marketCap', 'N/A')}\n"
            f"ROE：{info.get('returnOnEquity', 'N/A')}\n"
            f"营收增长率：{info.get('revenueGrowth', 'N/A')}\n"
            f"毛利率：{info.get('grossMargins', 'N/A')}\n"
            f"负债率：{info.get('debtToEquity', 'N/A')}\n"
            f"行业：{info.get('industry', 'N/A')}\n"
        )
    except Exception as e:
        return f"获取财务指标失败：{type(e).__name__}: {str(e)}"


@tool
def get_financial_indicator(symbol: str) -> str:
    """
    获取A股股票的核心财务指标，用于基本面分析。
    symbol: 股票代码，如 '600487'
    """
    try:
        import yfinance as yf
        yf_symbol = f"{symbol}.SS" if symbol.startswith('6') else f"{symbol}.SZ"
        ticker = yf.Ticker(yf_symbol)
        info = ticker.info

        return (
            f"股票：{info.get('longName', symbol)}（{symbol}）基本面指标\n"
            f"最新价：{info.get('currentPrice', 'N/A')}\n"
            f"市盈率(PE)：{info.get('trailingPE', 'N/A')}\n"
            f"市净率(PB)：{info.get('priceToBook', 'N/A')}\n"
            f"总市值：{info.get('marketCap', 'N/A')}\n"
            f"ROE：{info.get('returnOnEquity', 'N/A')}\n"
            f"营收增长率：{info.get('revenueGrowth', 'N/A')}\n"
            f"毛利率：{info.get('grossMargins', 'N/A')}\n"
            f"负债率：{info.get('debtToEquity', 'N/A')}\n"
            f"行业：{info.get('industry', 'N/A')}\n"
        )
    except Exception as e:
        return f"获取财务指标失败：{type(e).__name__}: {str(e)}"


@tool
def get_stock_history(symbol: str, days: int = 30) -> str:
    """获取A股股票最近N天的历史K线数据"""
    try:
        date_key = datetime.now().strftime("%Y%m%d%H")
        df = _get_stock_history_cached(symbol, days, date_key)

        if df.empty:
            return f"未找到股票 {symbol} 的历史数据"

        # 手动计算涨跌幅
        df["涨跌幅"] = df["收盘"].pct_change() * 100

        cols = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '涨跌幅']
        available_cols = [c for c in cols if c in df.columns]
        df = df[available_cols]

        summary = (
            f"股票 {symbol} 最近{len(df)}天K线数据：\n"
            f"期间最高价：{df['最高'].max():.2f}\n"
            f"期间最低价：{df['最低'].min():.2f}\n"
            f"最新收盘价：{df['收盘'].iloc[-1]:.2f}\n\n"
            f"最近10日明细：\n{df.tail(10).to_string(index=False)}"
        )
        return summary

    except Exception as e:
        return f"获取历史数据失败：{type(e).__name__}: {str(e)}"


@tool
def get_financial_indicator(symbol: str) -> str:
    """
    获取A股股票的核心财务指标，用于基本面分析。
    symbol: 股票代码，如 '600487'
    """
    try:
        import yfinance as yf
        yf_symbol = f"{symbol}.SS" if symbol.startswith('6') else f"{symbol}.SZ"
        ticker = yf.Ticker(yf_symbol)
        info = ticker.info

        return (
            f"股票：{info.get('longName', symbol)}（{symbol}）基本面指标\n"
            f"最新价：{info.get('currentPrice', 'N/A')}\n"
            f"市盈率(PE)：{info.get('trailingPE', 'N/A')}\n"
            f"市净率(PB)：{info.get('priceToBook', 'N/A')}\n"
            f"总市值：{info.get('marketCap', 'N/A')}\n"
            f"ROE：{info.get('returnOnEquity', 'N/A')}\n"
            f"营收增长率：{info.get('revenueGrowth', 'N/A')}\n"
            f"毛利率：{info.get('grossMargins', 'N/A')}\n"
            f"负债率：{info.get('debtToEquity', 'N/A')}\n"
            f"行业：{info.get('industry', 'N/A')}\n"
        )
    except Exception as e:
        return f"获取财务指标失败：{type(e).__name__}: {str(e)}"


@tool
def get_stock_news(symbol: str) -> str:
    """获取A股股票相关的最新新闻资讯"""
    try:
        time.sleep(1)  # 新闻接口也加延迟
        df = ak.stock_news_em(symbol=symbol)

        if df.empty:
            return f"未找到股票 {symbol} 的相关新闻"

        news_list = []
        for _, row in df.head(5).iterrows():
            news_list.append(f"【{row['发布时间']}】{row['新闻标题']}")

        return f"股票 {symbol} 最新资讯：\n" + "\n".join(news_list)

    except Exception as e:
        return f"获取新闻失败：{str(e)}"


ALL_TOOLS = [
    get_stock_price,
    get_stock_history,
    get_financial_indicator,
    get_stock_news,
]
