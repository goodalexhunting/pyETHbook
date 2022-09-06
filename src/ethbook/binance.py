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
from limit_level import LimitLevel
# https://binance-docs.github.io/apidocs/spot/en/#live-subscribing-unsubscribing-to-streams


class BinanceOrderBook(OrderBook):
    def __init__(self, bids: SortedDict, asks: SortedDict, live: Live) -> BinanceOrderBook:
        super().__init__(bids, asks, live)
        self.name = "Binance"
        self.last_update_id = None 
        self.orderbook_url = f"https://api.binance.com/api/v3/depth?symbol=ETHUSDT&limit=1000"
        self.ws_url = f"wss://stream.binance.com:9443/ws/ethusdt@depth"
        self.previous_update_id = 0
        self.exchange_colour = "#F3BA2F"
        
    def run(self) -> None:
        print("running binance orderbook")
        orderbook = requests.get(self.orderbook_url).json()
        
        self.process_orderbook_event(orderbook["bids"], self.bids)
        self.process_orderbook_event(orderbook["asks"], self.asks)
 

        self.last_update_id = orderbook["lastUpdateId"]
        ws = WebSocketApp(self.ws_url, on_message=self._wrap_callback(self._on_message), on_open=self._wrap_callback(self._on_message))
        ws.run_forever(dispatcher=rel)
    
    def process_orderbook_event(self, orderbook_data: list[list[str]], side: SortedDict[float, LimitLevel]) -> None:
        for price, quantity in orderbook_data:
            price = float(price)
            quantity = float(quantity)
            try:
                side[price].update_quantity(self.name, quantity)
            except KeyError:
                side[price] = LimitLevel()
                side[price].update_quantity(self.name, quantity)
            if -0.000000000001 < side[price].total_quantity < 0.000000000001:
                side.pop(price)


    def _on_message(self, ws: WebSocketApp, message) -> None:
        message = json.loads(message)
        #print("received message")
        if int(message['u']) <= self.last_update_id:
            return
        self.process_orderbook_event(message['b'], self.bids)
        self.process_orderbook_event(message['a'], self.asks)
        
        self.live.update(self._generate_table())
        # print(F"BEST TEMP BID: {max(self.temp_bids.keys())} QTY: {self.temp_bids[max(self.temp_bids.keys())]}  BEST TEMP ASK: {min(self.temp_asks.keys())} QTY: {self.temp_asks[min(self.temp_asks.keys())]}")
        # print(F"BEST BID: {max(self.bids.keys())} QTY: {self.bids[max(self.bids.keys())].total_quantity} BEST ASK: {min(self.asks.keys())} QTY: {self.asks[min(self.asks.keys())].total_quantity}")
        self.previous_update_id = int(message['u'])
    
    def _on_open(self, ws, message) -> None:
        print("Opening conection")

def main() -> None:
    client: BinanceOrderBook = BinanceOrderBook()
    client.run()

if __name__ == "__main__":
    main()


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
    




