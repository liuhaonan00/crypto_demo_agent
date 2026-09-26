"""工具注册：OpenAI function 定义 + 名称分发。"""
from . import market, news

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_price",
            "description": "查询最新成交价格，现货和合约通用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "交易对，如 BTC/USDT、ETH/USDT"},
                    "market_type": {"type": "string", "enum": ["spot", "futures"],
                                    "description": "spot 现货 / futures 合约，默认 spot"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_candles",
            "description": "查询 K 线，包含开高低收、成交量。",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "交易对，如 BTC/USDT"},
                    "market_type": {"type": "string", "enum": ["spot", "futures"], "description": "默认 spot"},
                    "interval": {"type": "string", "enum": ["1m", "5m", "15m", "1h", "4h", "1d"], "description": "默认 1h"},
                    "limit": {"type": "integer", "description": "返回根数，默认 100，最大 1500"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_ema",
            "description": "计算指数移动平均 EMA，返回最新值及最近若干值。",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "交易对，如 BTC/USDT"},
                    "market_type": {"type": "string", "enum": ["spot", "futures"], "description": "默认 spot"},
                    "interval": {"type": "string", "enum": ["1m", "5m", "15m", "1h", "4h", "1d"], "description": "默认 1h"},
                    "period": {"type": "integer", "description": "EMA 周期，常用 20，默认 20"},
                    "limit": {"type": "integer", "description": "取多少根 K 线计算，默认 200"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_rsi",
            "description": "计算相对强弱指标 RSI（Wilder 平滑），返回最新值及最近若干值。",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "交易对，如 BTC/USDT"},
                    "market_type": {"type": "string", "enum": ["spot", "futures"], "description": "默认 spot"},
                    "interval": {"type": "string", "enum": ["1m", "5m", "15m", "1h", "4h", "1d"], "description": "默认 1h"},
                    "period": {"type": "integer", "description": "RSI 周期，常用 14，默认 14"},
                    "limit": {"type": "integer", "description": "取多少根 K 线计算，默认 200"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_macd",
            "description": "计算 MACD（快慢线差值 + 信号线 + 柱状图），返回最新值及最近若干值。",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "交易对，如 BTC/USDT"},
                    "market_type": {"type": "string", "enum": ["spot", "futures"], "description": "默认 spot"},
                    "interval": {"type": "string", "enum": ["1m", "5m", "15m", "1h", "4h", "1d"], "description": "默认 1h"},
                    "fast": {"type": "integer", "description": "快线周期，默认 12"},
                    "slow": {"type": "integer", "description": "慢线周期，默认 26"},
                    "signal": {"type": "integer", "description": "信号线周期，默认 9"},
                    "limit": {"type": "integer", "description": "取多少根 K 线计算，默认 200"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_funding_rate",
            "description": "查询合约资金费率，含结算时间。",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "交易对，如 BTC/USDT"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_mark_price",
            "description": "查询合约标记价格与指数价格。",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "交易对，如 BTC/USDT"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_open_interest",
            "description": "查询合约持仓量 Open Interest。",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "交易对，如 BTC/USDT"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_news",
            "description": "搜索加密货币相关新闻（来源 CryptoPanic）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词，如 bitcoin、ethereum、DeFi"},
                    "currencies": {"type": "string", "description": "按币种过滤，如 BTC,ETH，可留空"},
                    "limit": {"type": "integer", "description": "返回条数，默认 10，最大 50"},
                },
                "required": [],
            },
        },
    },
]


def execute_tool(name, args, settings):
    """执行工具并返回结果 dict。settings 用于注入 CryptoPanic key。"""
    try:
        if name == "get_price":
            return market.get_price(args.get("symbol", "BTC/USDT"), args.get("market_type", "spot"))
        if name == "get_candles":
            return market.get_candles(args.get("symbol", "BTC/USDT"), args.get("market_type", "spot"),
                                      args.get("interval", "1h"), args.get("limit", 100))
        if name == "get_ema":
            return market.get_ema(args.get("symbol", "BTC/USDT"), args.get("market_type", "spot"),
                                  args.get("interval", "1h"), args.get("period", 20), args.get("limit", 200))
        if name == "get_rsi":
            return market.get_rsi(args.get("symbol", "BTC/USDT"), args.get("market_type", "spot"),
                                  args.get("interval", "1h"), args.get("period", 14), args.get("limit", 200))
        if name == "get_macd":
            return market.get_macd(args.get("symbol", "BTC/USDT"), args.get("market_type", "spot"),
                                   args.get("interval", "1h"), args.get("fast", 12),
                                   args.get("slow", 26), args.get("signal", 9), args.get("limit", 200))
        if name == "get_funding_rate":
            return market.get_funding_rate(args.get("symbol", "BTC/USDT"))
        if name == "get_mark_price":
            return market.get_mark_price(args.get("symbol", "BTC/USDT"))
        if name == "get_open_interest":
            return market.get_open_interest(args.get("symbol", "BTC/USDT"))
        if name == "search_news":
            return news.search_news(settings.cryptopanic_key, args.get("query", ""),
                                    args.get("currencies"), args.get("limit", 10))
    except Exception as exc:
        return {"error": "工具执行异常：" + str(exc)}
    return {"error": "未知工具：" + str(name)}
