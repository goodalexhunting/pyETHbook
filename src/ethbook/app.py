from __future__ import annotations
from threading import Thread
from websocket import WebSocketApp, enableTrace
import json
import requests
from sortedcontainers import SortedDict
from tabulate import tabulate
from rich.table import Table
from textual import events
from textual.app import App
from textual.widgets import ScrollView
import random
import time
from rich.live import Live
from rich.table import Table
# https://binance-docs.github.io/apidocs/spot/en/#live-subscribing-unsubscribing-to-streams


class BinanceOrderBook():
    
    def __init__(self, limit = 20, delay = '100ms', pair = "btcusdt") -> BinanceOrderBook:
        self.bids = SortedDict()
        self.asks = SortedDict()
        self.last_update_id:int = None 
        self.orderbook_url = f"https://api.binance.com/api/v3/depth?symbol={pair.upper()}&limit={limit}"
        self.ws_url = f"wss://stream.binance.com:9443/ws/{pair}@depth@{delay}"
        self.previous_update_id = None

    def run(self) -> None:
        orderbook = requests.get(self.orderbook_url).json()
        for price_level in orderbook["bids"]:
            self.bids[float(price_level[0])] = float(price_level[1])
        
        for price_level in orderbook["asks"]:
            self.asks[float(price_level[0])] = float(price_level[1])
        print(f"Best bid: {self.bids.keys()[-1]}:{self.bids.values()[-1]}, Best Ask: {self.asks.keys()[0]}:{self.asks.values()[0]}")
        self.last_update_id = orderbook["lastUpdateId"]
        ws = WebSocketApp(self.ws_url, on_message=self._wrap_callback(self._on_message), on_open=self._wrap_callback(self._on_message))
        
        self.live = Live(self._generate_table())
        self.live.start()
        ws.run_forever()


    def _generate_table(self) -> Table:
        table = Table()
        table.add_column("Price")
        table.add_column("Quantity")
        table.add_column("Price")
        table.add_column("Quantity")
        for (bid_level, ask_level) in zip(reversed(self.bids.items()[:]), self.asks.items()[:]): 
            table.add_row(
            f"[green]{bid_level[0]}", f"[green]{bid_level[1]}",f"[red]{ask_level[0]}",f"[red]{ask_level[1]}"
            )
        return table
    
    def _wrap_callback(self,f):
        def wrapped_f(ws, *args, **kwargs):
            try:
                f(ws, *args, **kwargs)
            except Exception as e:
                raise Exception(f"Error running websocket callback: {e}")
        return wrapped_f


    def _on_message(self, ws, message) -> None:
        message = json.loads(message)
        
        if message['u'] <= self.last_update_id:
            print(f"{message['u']=} {self.last_update_id=}")
            return

        for price_level, new_quantity in message['b']:
            price_level = float(price_level)
            self.bids[price_level] = float(new_quantity)
            if self.bids[price_level] == float(0):
                self.bids.pop(price_level)

        for price_level, new_quantity in message['a']: 
            price_level = float(price_level)
            self.asks[price_level] = float(new_quantity)
            if self.asks[price_level] == float(0):
                self.asks.pop(price_level)
        
        self.previous_update_id = message['u']
        self.live.update(self._generate_table())
        print(f"{len(self.asks)=}")

    def _on_open(self, ws, message) -> None:
        print("Opening conection")

def main() -> None:
    client: BinanceOrderBook = BinanceOrderBook()
    client.run()

if __name__ == "__main__":
    main()

#TODO
#1) get current state of orderbook, and store it in two sorted containers
#2) listen to stream
#3) for each depthUpdate, update orderbook
#4) 

# "https://api.binance.com/api/v3/depth/exchangeInfo?symbol=BNBBTC"
# {
#   "e": "depthUpdate", // Event type
#   "E": 123456789,     // Event time
#   "s": "BNBBTC",      // Symbol
#   "U": 157,           // First update ID in event
#   "u": 160,           // Final update ID in event
#   "b": [              // seBids to be updated
#     [
#       "0.0024",       // Price level to be updated
#       "10"            // Quantity
#     ]
#   ],
#   "a": [              // self.Asks to be updated
#     [
#       "0.0026",       // Price level to be updated
#       "100"           // Quantity
#     ]
#   ]
# }
    




