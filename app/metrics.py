from prometheus_client import Counter, Gauge, Histogram, start_http_server

trades_total = Counter("trades_total", "Total trades", ["symbol", "side"])
equity_gauge = Gauge("equity", "Equity value")
lat_hist = Histogram("strategy_latency_ms", "Strategy loop latency (ms)")

def expose(port=8000):
    start_http_server(port)
