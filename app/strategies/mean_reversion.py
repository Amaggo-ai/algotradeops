# app/strategies/mean_reversion.py
import pandas as pd
import numpy as np  # optional, useful for experiments

class Strategy:
    """
    Mean Reversion Strategy
    -----------------------
    - Compute moving average (MA) and std over a lookback window.
    - Buy when close < MA - N*std (expect reversion up).
    - Sell when close > MA + N*std (expect reversion down).
    """

    name = "mean_reversion"
    params = {
        "lookback": 20,
        "std_mult": 2.0,
    }

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Validate input
        if "close" not in df.columns:
            raise ValueError("Input DataFrame must contain a 'close' column.")

        lookback = int(self.params["lookback"])
        std_mult = float(self.params["std_mult"])

        # Indicators
        df["ma"] = df["close"].rolling(lookback).mean()
        df["std"] = df["close"].rolling(lookback).std(ddof=0)

        df["upper"] = df["ma"] + std_mult * df["std"]
        df["lower"] = df["ma"] - std_mult * df["std"]

        # Signals: +1 = long, -1 = short, 0 = flat
        df["signal"] = 0
        df.loc[df["close"] < df["lower"], "signal"] = 1
        df.loc[df["close"] > df["upper"], "signal"] = -1

        df["signal"] = df["signal"].fillna(0)

        return df[["close", "ma", "upper", "lower", "signal"]]
