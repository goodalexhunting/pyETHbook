from __future__ import annotations
from threading import Thread
from ethbook.order_book import OrderBook
from websocket import WebSocketApp, enableTrace, create_connection
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

# https://docs.cloud.coinbase.com/exchange/docs/websocket-overview

#TODO Checksum to make sure that our state is correct
#TODO Timestamp maybe

class CoinbaseOrderBook(OrderBook):
    def __init__(self, combined_bids: SortedDict, combined_asks: SortedDict, live: Live) -> CoinbaseOrderBook:
        super().__init__(combined_bids, combined_asks, live)
        self.ws_url = f"wss://ws-feed.exchange.coinbase.com"
        self.timestamp = None
        self.exchange_colour = "#1554f0"

    def run(self) -> None:  
        ws = WebSocketApp(self.ws_url, on_message=self._wrap_callback(self._on_message), on_open=self._wrap_callback(self._on_open))
        self.live = Live(self._generate_table())
        self.live.start()
        ws.run_forever()

    def _update_orderbook(self, message) -> None:
        for side, price_level, new_quantity in message["changes"]:
            
            book_side = None
            if side == "buy" :
                book_side = self.bids
            else:
                book_side = self.asks
            if float(new_quantity) == 0:
                book_side.pop(price_level)
                continue
            book_side[float(price_level)] = float(new_quantity)
          
    def _populate_orderbook(self, message) -> None:
        for price_level, new_quantity in message['bids']:
            price_level = float(price_level)
            self.bids[price_level] = float(new_quantity)
            
        for price_level, new_quantity in message['asks']: 
            price_level = float(price_level)
            self.asks[price_level] = float(new_quantity)
            
    def _on_message(self, ws, message) -> None:  
        # print(message)
        message = json.loads(message)
        if message["type"] == "snapshot":
            self._populate_orderbook(message)
            
        elif message["type"] == "l2update":
            self._update_orderbook(message)
        elif message["type"] == "subscribed":
            print("subscribe to goodalexhunting")
            return
        else: 
            return
        self.live.update(self._generate_table())
        
    def _on_open(self, ws) -> None:
        print("opening connection")
        ws.send(json.dumps({
                                "type": "subscribe",
                                "product_ids": [
                                    "BTC-USDT"
                                ],
                                "channels": ["level2"]}))

def main() -> None:
    client: CoinbaseOrderBook = CoinbaseOrderBook()
    client.run()

if __name__ == "__main__":
    main()




    




