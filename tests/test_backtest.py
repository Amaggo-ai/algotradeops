import pandas as pd
import numpy as np

from app.backtest.engine import backtest

def test_backtest_all_long_increasing_prices():
    # Close rises 100 → 104 over 5 bars
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    df = pd.DataFrame({"close": [100, 101, 102, 103, 104]}, index=idx)

    # Always long (signal=1)
    signals = pd.DataFrame({"signal": 1}, index=idx)

    res = backtest(df, signals, cash=100_000)
    # With pos=signal.shift(), we capture returns from t1..end.
    expected = 100_000 * (104 / 100)  # telescopes to last/first
    assert isinstance(res, dict)
    assert "equity_end" in res and "equity_curve" in res
    assert abs(res["equity_end"] - expected) < 1e-6
    assert len(res["equity_curve"]) == len(df.dropna())


def test_backtest_no_position_equity_unchanged():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    df = pd.DataFrame({"close": [100, 99, 98, 102, 101]}, index=idx)
    signals = pd.DataFrame({"signal": 0}, index=idx)  # never take a position

    res = backtest(df, signals, cash=50_000)
    assert abs(res["equity_end"] - 50_000) < 1e-6
    assert (res["equity_curve"] >= 0).all()


def test_backtest_requires_signal_column():
    idx = pd.date_range("2024-01-01", periods=3, freq="D")
    df = pd.DataFrame({"close": [100, 101, 102]}, index=idx)
    bad_signals = pd.DataFrame({"not_signal": [0, 1, 0]}, index=idx)

    # Expect KeyError when 'signal' is missing in join
    try:
        backtest(df, bad_signals, cash=10_000)
        assert False, "Expected KeyError due to missing 'signal' column"
    except KeyError:
        assert True
