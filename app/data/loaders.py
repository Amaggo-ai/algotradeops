import pandas as pd
from datetime import datetime, timedelta
import os

def load_csv(path):
    return pd.read_csv(path, parse_dates=["timestamp"]).set_index("timestamp").sort_index()

def load_dummy_prices(symbol, days=200):
    import numpy as np
    idx = pd.date_range(end=datetime.utcnow(), periods=days, freq="h")
    prices = 100 + np.cumsum(np.random.normal(0, 0.5, len(idx)))
    return pd.DataFrame({"close": prices}, index=idx)
