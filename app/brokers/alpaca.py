import requests, json

class AlpacaBroker:
    def __init__(self, key, secret, base):
        self.key, self.secret, self.base = key, secret, base
        self.h = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret}

    def submit_order(self, symbol, side, qty):
        url = f"{self.base}/v2/orders"
        data = {"symbol": symbol, "side": side, "type": "market", "qty": qty, "time_in_force": "day"}
        r = requests.post(url, headers=self.h, json=data, timeout=15)
        r.raise_for_status()
        return r.json()

    def get_positions(self):
        r = requests.get(f"{self.base}/v2/positions", headers=self.h, timeout=15)
        r.raise_for_status()
        return r.json()

    def get_cash(self):
        r = requests.get(f"{self.base}/v2/account", headers=self.h, timeout=15)
        r.raise_for_status()
        return float(r.json()["cash"])
