class SimBroker:
    """
    Super-simple simulated broker:
      - Tracks cash and position per symbol
      - Applies fills at the provided price
      - Can compute mark-to-market equity given latest prices
    """
    def __init__(self, cash=100000):
        self.cash = float(cash)
        self.positions = {}  # { symbol: qty }

    def submit_order(self, symbol: str, side: str, qty: int, price: float):
        qty = int(qty)
        price = float(price)
        notional = qty * price

        if side == "buy":
            self.cash -= notional
            self.positions[symbol] = self.positions.get(symbol, 0) + qty
        elif side == "sell":
            self.cash += notional
            self.positions[symbol] = self.positions.get(symbol, 0) - qty
        else:
            raise ValueError(f"Unknown side: {side}")

    def get_positions(self):
        return dict(self.positions)

    def get_cash(self):
        return float(self.cash)

    def get_equity(self, prices: dict):
        """cash + sum(qty * last_price) for each symbol present in `prices`"""
        mv = 0.0
        for sym, qty in self.positions.items():
            px = float(prices.get(sym, 0.0))
            mv += qty * px
        return float(self.cash + mv)
