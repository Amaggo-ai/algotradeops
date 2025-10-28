import os

class Settings:
    MODE = os.getenv("MODE", "backtest")  # backtest|paper|sim
    STRATEGY = os.getenv("STRATEGY", "sma_cross")
    SYMBOLS = os.getenv("SYMBOLS", "AAPL,MSFT").split(",")
    INTERVAL = os.getenv("INTERVAL", "1h")
    CASH = float(os.getenv("CASH", "100000"))
    # Alpaca (paper)
    ALPACA_KEY = os.getenv("ALPACA_KEY", "")
    ALPACA_SECRET = os.getenv("ALPACA_SECRET", "")
    ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", 
"https://paper-api.alpaca.markets")

settings = Settings()
