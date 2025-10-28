import os, time
import psycopg2
from datetime import datetime, timezone
from app.data.loaders import load_dummy_prices

PG_DSN = os.getenv("PG_DSN", "dbname=trader user=trader password=trader host=postgres port=5432")
SYMBOL = os.getenv("SYMBOL", "AAPL")
CANDLE_SECONDS = int(os.getenv("CANDLE_SECONDS", "60"))

def bucket(ts, sec=60):
    return ts.replace(second=0, microsecond=0, tzinfo=timezone.utc)

def main():
    conn = psycopg2.connect(PG_DSN)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ohlc (
      symbol text NOT NULL,
      bucket timestamptz NOT NULL,
      open double precision NOT NULL,
      high double precision NOT NULL,
      low  double precision NOT NULL,
      close double precision NOT NULL,
      volume double precision NOT NULL DEFAULT 0,
      PRIMARY KEY (symbol, bucket)
    );""")
    print("[COLLECTOR] writing OHLC bars to Postgres")

    last_b = None
    o=h=l=c=vol=None

    while True:
        price = float(load_dummy_prices(SYMBOL, days=1)["close"].iloc[-1])
        now = datetime.now(timezone.utc)
        b = bucket(now, CANDLE_SECONDS)

        if last_b is None or b != last_b:
            if last_b is not None:
                cur.execute("""
                INSERT INTO ohlc(symbol,bucket,open,high,low,close,volume)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (symbol,bucket) DO UPDATE
                  SET open=EXCLUDED.open, high=EXCLUDED.high, low=EXCLUDED.low,
                      close=EXCLUDED.close, volume=EXCLUDED.volume
                """, (SYMBOL, last_b, o, h, l, c, vol))
            last_b = b
            o=h=l=c=price
            vol = 1.0
        else:
            c = price
            h = max(h, price)
            l = min(l, price)
            vol += 1.0

        time.sleep(5)

if __name__ == "__main__":
    main()
