"""Binance 行情工具（公开 REST，无需 key）：价格 / K线 / 指标 / 资金费率 / 标记价 / 持仓量。"""
import httpx

from .indicators import ema_series, macd_series, rsi_series

SPOT_REST = "https://api.binance.com/api/v3"
FUTURES_REST = "https://fapi.binance.com/fapi/v1"
INTERVALS = {"1m", "5m", "15m", "1h", "4h", "1d"}


def _normalize(symbol: str) -> str:
    return (symbol or "").replace("/", "").replace("-", "").replace("_", "").upper().strip()


def _get(url, params=None, timeout=20):
    try:
        r = httpx.get(url, params=params, timeout=timeout)
    except httpx.HTTPError as exc:
        return {"error": "请求 Binance 失败：" + str(exc)}
    if r.status_code != 200:
        return {"error": "Binance 返回 %s：%s" % (r.status_code, r.text[:200])}
    try:
        return r.json()
    except Exception as exc:
        return {"error": "解析 Binance 响应失败：" + str(exc)}


def _series_result(values):
    vals = [round(float(v), 6) for v in values if v is not None]
    if not vals:
        return {"error": "数据不足，无法计算"}
    return {"latest": vals[-1], "recent": vals[-10:]}


def get_price(symbol="BTC/USDT", market_type="spot"):
    sym = _normalize(symbol)
    base = SPOT_REST if market_type == "spot" else FUTURES_REST
    data = _get(base + "/ticker/price", {"symbol": sym})
    if isinstance(data, dict) and "error" in data:
        return data
    return {"symbol": sym, "market_type": market_type, "price": data.get("price")}


def get_candles(symbol="BTC/USDT", market_type="spot", interval="1h", limit=100):
    sym = _normalize(symbol)
    if interval not in INTERVALS:
        interval = "1h"
    limit = max(1, min(int(limit or 100), 1500))
    base = SPOT_REST if market_type == "spot" else FUTURES_REST
    data = _get(base + "/klines", {"symbol": sym, "interval": interval, "limit": limit})
    if isinstance(data, dict) and "error" in data:
        return data
    candles = [{
        "openTime": c[0], "open": c[1], "high": c[2], "low": c[3],
        "close": c[4], "volume": c[5], "closeTime": c[6],
    } for c in data]
    return {"symbol": sym, "market_type": market_type, "interval": interval, "candles": candles}


def _closes(symbol, market_type, interval, limit):
    res = get_candles(symbol, market_type, interval, limit)
    if isinstance(res, dict) and "error" in res:
        return res
    return [float(c["close"]) for c in res["candles"]]


def get_ema(symbol="BTC/USDT", market_type="spot", interval="1h", period=20, limit=200):
    closes = _closes(symbol, market_type, interval, limit)
    if isinstance(closes, dict):
        return closes
    return {
        "symbol": _normalize(symbol), "market_type": market_type,
        "interval": interval, "period": period,
        **_series_result(ema_series(closes, period)),
    }


def get_rsi(symbol="BTC/USDT", market_type="spot", interval="1h", period=14, limit=200):
    closes = _closes(symbol, market_type, interval, limit)
    if isinstance(closes, dict):
        return closes
    return {
        "symbol": _normalize(symbol), "market_type": market_type,
        "interval": interval, "period": period,
        **_series_result(rsi_series(closes, period)),
    }


def get_macd(symbol="BTC/USDT", market_type="spot", interval="1h",
             fast=12, slow=26, signal=9, limit=200):
    closes = _closes(symbol, market_type, interval, limit)
    if isinstance(closes, dict):
        return closes
    dif, sig, hist = macd_series(closes, fast, slow, signal)
    return {
        "symbol": _normalize(symbol), "market_type": market_type,
        "interval": interval, "fast": fast, "slow": slow, "signal": signal,
        "dif": _series_result(dif), "signal": _series_result(sig), "histogram": _series_result(hist),
    }


def get_funding_rate(symbol="BTC/USDT"):
    sym = _normalize(symbol)
    data = _get(FUTURES_REST + "/fundingRate", {"symbol": sym, "limit": 1})
    if isinstance(data, dict) and "error" in data:
        return data
    if isinstance(data, list) and data:
        return {"symbol": sym, "fundingRate": data[0].get("fundingRate"),
                "fundingTime": data[0].get("fundingTime")}
    return {"symbol": sym, "error": "无资金费率数据"}


def get_mark_price(symbol="BTC/USDT"):
    sym = _normalize(symbol)
    data = _get(FUTURES_REST + "/premiumIndex", {"symbol": sym})
    if isinstance(data, dict) and "error" in data:
        return data
    return {"symbol": sym, "markPrice": data.get("markPrice"), "indexPrice": data.get("indexPrice")}


def get_open_interest(symbol="BTC/USDT"):
    sym = _normalize(symbol)
    data = _get(FUTURES_REST + "/openInterest", {"symbol": sym})
    if isinstance(data, dict) and "error" in data:
        return data
    return {"symbol": sym, "openInterest": data.get("openInterest"), "time": data.get("time")}
