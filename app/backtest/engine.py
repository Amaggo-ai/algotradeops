import pandas as pd

def backtest(df, signals, cash=100000, fee=0.0):
    df = df.join(signals["signal"]).dropna().copy()
    df["pos"] = df["signal"].shift().fillna(0)
    df["ret"] = df["close"].pct_change().fillna(0)
    df["pnl"] = df["pos"] * df["ret"]
    equity = (1 + df["pnl"]).cumprod() * cash
    return {"equity_end": float(equity.iloc[-1]), "equity_curve": equity}
