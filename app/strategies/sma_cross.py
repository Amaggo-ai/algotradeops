import pandas as pd

class Strategy:
    name = "sma_cross"
    params = {"fast": 10, "slow": 30}

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "close" not in df.columns:
            raise ValueError("Input DataFrame must contain a 'close' column.")
        fast = int(self.params["fast"])
        slow = int(self.params["slow"])
        if fast <= 0 or slow <= 0:
            raise ValueError("Parameters 'fast' and 'slow' must be > 0.")
        df["fast"] = df["close"].rolling(fast).mean()
        df["slow"] = df["close"].rolling(slow).mean()
        df["signal"] = 0
        df.loc[df["fast"] > df["slow"], "signal"] = 1
        df.loc[df["fast"] < df["slow"], "signal"] = -1
        return df
