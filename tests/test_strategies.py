import pandas as pd
import numpy as np
import importlib
import pytest

def test_sma_cross_generates_signals_trending_up():
    sma_mod = importlib.import_module("app.strategies.sma_cross")
    Strat = sma_mod.Strategy
    strat = Strat()
    # Make fast/slow shorter for a tiny sample
    strat.params["fast"] = 3
    strat.params["slow"] = 5

    idx = pd.date_range("2024-01-01", periods=20, freq="D")
    # Strictly increasing close → fast > slow near the end
    df = pd.DataFrame({"close": np.linspace(100, 120, len(idx))}, index=idx)

    out = strat.generate_signals(df)
    assert "signal" in out.columns
    # Last signal should be long (1) for an uptrend
    assert out["signal"].iloc[-1] in (0, 1)
    assert out["signal"].iloc[-1] == 1


def test_mean_reversion_triggers_on_extremes():
    mr_mod = importlib.import_module("app.strategies.mean_reversion")
    Strat = mr_mod.Strategy
    strat = Strat()
    # Make it very sensitive so we can trigger in a small sample
    strat.params["lookback"] = 5
    strat.params["std_mult"] = 0.5

    # Construct a series hovering around 100, then an undercut and an overextension
    idx = pd.date_range("2024-01-01", periods=15, freq="D")
    base = [100, 100.2, 100.1, 100.3, 100.2, 100.1, 100.0, 100.2, 100.1]
    # Force a deep dip and a spike to cross bands
    series = base + [98.5, 100.0, 100.2, 100.1, 101.8, 102.2]
    df = pd.DataFrame({"close": series}, index=idx)

    out = strat.generate_signals(df)
    assert set(["ma", "upper", "lower", "signal"]).issubset(out.columns)

    # Find the dip index and spike index
    dip_idx = df["close"].idxmin()
    spike_idx = df["close"].idxmax()

    # Around the dip, we expect a +1 signal (buy)
    # Note: bands need lookback data, so allow +/-1 around the exact index
    window_dip = out.loc[dip_idx - pd.Timedelta(days=1): dip_idx + pd.Timedelta(days=1)]["signal"]
    assert (window_dip == 1).any()

    # Around the spike, we expect a -1 signal (sell)
    window_spike = out.loc[spike_idx - pd.Timedelta(days=1): spike_idx + pd.Timedelta(days=1)]["signal"]
    assert (window_spike == -1).any()


def test_strategies_require_close_column():
    sma = importlib.import_module("app.strategies.sma_cross").Strategy()
    mr = importlib.import_module("app.strategies.mean_reversion").Strategy()

    bad_df = pd.DataFrame({"price": [1, 2, 3]})  # missing 'close'
    with pytest.raises(ValueError):
        sma.generate_signals(bad_df)
    with pytest.raises(ValueError):
        mr.generate_signals(bad_df)
