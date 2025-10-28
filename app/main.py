import importlib, os, time
from app.config import settings
from app.data.loaders import load_dummy_prices
from app.backtest.engine import backtest
from app.metrics import expose, trades_total, equity_gauge, lat_hist
from app.brokers.simulated import SimBroker
from app.brokers.alpaca import AlpacaBroker

def load_strategy(name):
    m = importlib.import_module(f"app.strategies.{name}")
    return m.Strategy()

def get_broker():
    if settings.MODE == "paper":
        return AlpacaBroker(settings.ALPACA_KEY, settings.ALPACA_SECRET, settings.ALPACA_BASE_URL)
    return SimBroker(cash=settings.CASH)

def run_backtest():
    strat = load_strategy(settings.STRATEGY)
    df = load_dummy_prices(settings.SYMBOLS[0])
    sig = strat.generate_signals(df)
    res = backtest(df, sig, cash=settings.CASH)
    equity_gauge.set(res["equity_end"])
    print(f"[BACKTEST] Strategy={settings.STRATEGY} | End Equity=${res['equity_end']:.2f}")

def run_live():
    expose(8000)
    broker = get_broker()
    strat = load_strategy(settings.STRATEGY)
    symbol = settings.SYMBOLS[0]
    print(f"[LIVE] Running {settings.STRATEGY} in {settings.MODE} mode for {symbol}")

    while True:
        t0 = time.time()

        # Get latest data & signal
        df = load_dummy_prices(symbol, days=200)  # swap with real feed later
        last_row = strat.generate_signals(df).iloc[-1]
        sig = int(last_row["signal"])
        price = float(df["close"].iloc[-1])

        # Place an order if we have a signal
        side = "buy" if sig > 0 else ("sell" if sig < 0 else None)
        if side:
            trades_total.labels(symbol=symbol, side=side).inc()
            # SimBroker expects price; AlpacaBroker does not. Try price first, fall back if needed.
            try:
                broker.submit_order(symbol, side, qty=1, price=price)
            except TypeError:
                broker.submit_order(symbol, side, qty=1)

        # Mark-to-market equity metric
        try:
            equity = broker.get_equity({symbol: price})
        except AttributeError:
            # For brokers without get_equity(), fall back to cash
            equity = broker.get_cash()

        equity_gauge.set(equity)
        lat_hist.observe((time.time() - t0) * 1000)
        time.sleep(30)

if __name__ == "__main__":
    if settings.MODE == "backtest":
        run_backtest()
    else:
        run_live()
