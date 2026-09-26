"""技术指标计算：EMA / RSI / MACD（纯 Python，无第三方依赖）。"""


def ema_series(values, period):
    """返回与 values 等长的 EMA 列表，前 period-1 个为 None。"""
    n = len(values)
    if n < period:
        return [None] * n
    k = 2.0 / (period + 1)
    seed = sum(values[:period]) / period
    out = [None] * (period - 1) + [seed]
    prev = seed
    for v in values[period:]:
        prev = v * k + prev * (1 - k)
        out.append(prev)
    return out


def rsi_series(values, period=14):
    """Wilder 平滑 RSI，返回与 values 等长的列表，前 period 个为 None。"""
    n = len(values)
    if n <= period:
        return [None] * n
    gains = [0.0] * (n - 1)
    losses = [0.0] * (n - 1)
    for i in range(1, n):
        diff = values[i] - values[i - 1]
        gains[i - 1] = max(diff, 0.0)
        losses[i - 1] = max(-diff, 0.0)

    def _rsi(ag, al):
        if al == 0:
            return 100.0
        rs = ag / al
        return 100.0 - 100.0 / (1.0 + rs)

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    out = [None] * period
    out.append(_rsi(avg_gain, avg_loss))
    for i in range(period, n - 1):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        out.append(_rsi(avg_gain, avg_loss))
    return out


def macd_series(values, fast=12, slow=26, signal=9):
    """返回 (dif, signal, hist) 三个与 values 等长的列表。"""
    n = len(values)
    ef = ema_series(values, fast)
    es = ema_series(values, slow)
    dif = [None] * n
    for i in range(n):
        if ef[i] is not None and es[i] is not None:
            dif[i] = ef[i] - es[i]

    valid = [v for v in dif if v is not None]
    sig_vals = ema_series(valid, signal)
    sig = [None] * n
    k = 0
    for i in range(n):
        if dif[i] is not None:
            sig[i] = sig_vals[k]
            k += 1

    hist = [None] * n
    for i in range(n):
        if dif[i] is not None and sig[i] is not None:
            hist[i] = dif[i] - sig[i]
    return dif, sig, hist
