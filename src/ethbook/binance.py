from __future__ import annotations
from threading import Thread
from ethbook.order_book import OrderBook
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
import rel
# https://binance-docs.github.io/apidocs/spot/en/#live-subscribing-unsubscribing-to-streams


class BinanceOrderBook(OrderBook):
    def __init__(self, bids: SortedDict, asks: SortedDict, live: Live) -> BinanceOrderBook:
        super().__init__(bids, asks, live)
        self.name = "Binance"
        self.last_update_id:int = None 
        self.orderbook_url = f"https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=1000"
        self.ws_url = f"wss://stream.binance.com:9443/ws/btcusdt@depth@100ms"
        self.previous_update_id = None
        self.exchange_colour = "#F3BA2F"

    def run(self) -> None:
        print("running binance orderbook")
        orderbook = requests.get(self.orderbook_url).json()
        for price_level in orderbook["bids"]:
            self.bids[float(price_level[0])] = (float(price_level[1]), self.name)
        
        for price_level in orderbook["asks"]:
            self.asks[float(price_level[0])] = (float(price_level[1]), self.name)
        self.last_update_id = orderbook["lastUpdateId"]
        ws = WebSocketApp(self.ws_url, on_message=self._wrap_callback(self._on_message), on_open=self._wrap_callback(self._on_message))
        
        ws.run_forever(dispatcher=rel)
        

    def _on_message(self, ws: WebSocketApp, message) -> None:
        message = json.loads(message)
        # print("received message")
        if message['u'] <= self.last_update_id:
            # print(f"{message['u']=} {self.last_update_id=}")
            return

        for price_level, new_quantity in message['b']:
            price_level = float(price_level)
            self.bids[price_level] = (float(new_quantity),self.name)
            if self.bids[price_level][0] == float(0):
                self.bids.pop(price_level)

        for price_level, new_quantity in message['a']: 
            price_level = float(price_level)
            self.asks[price_level] = (float(new_quantity), self.name)
            if self.asks[price_level][0] == float(0):
                self.asks.pop(price_level)
        
        self.previous_update_id = message['u']
        self.live.update(self._generate_table())

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
    




