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

# https://docs.ftx.com/#orderbooks

#TODO Checksum to make sure that our state is correct
#TODO Timestamp maybe

class FtxOrderBook(OrderBook):
    def __init__(self, combined_bids: SortedDict, combined_asks: SortedDict, live: Live) -> FtxOrderBook:
        super().__init__(combined_bids, combined_asks, live)
        self.name = "FTX"
        self.ws_url = f"wss://ftx.com/ws/"
        self.timestamp = None
        self.exchange_colour = "#11A9BC"

    def run(self) -> None:
        ws = WebSocketApp(self.ws_url, on_message=self._wrap_callback(self._on_message), on_open=self._wrap_callback(self._on_open))
        ws.run_forever()

    def _update_orderbook(self, message) -> None:
        for price_level, new_quantity in message["data"]['bids']:
            price_level = float(price_level)
            self.bids[price_level] = (float(new_quantity), self.name)
            if self.bids[price_level][0] == float(0):
                    self.bids.pop(price_level)

        for price_level, new_quantity in message["data"]['asks']:
            price_level = float(price_level)
            self.asks[price_level] = (float(new_quantity), self.name)
            if self.asks[price_level][0] == float(0):
                self.asks.pop(price_level)
        
    def _populate_orderbook(self, message) -> None:
        for price_level, new_quantity in message["data"]['bids']:
            price_level = float(price_level)
            self.bids[price_level] = (float(new_quantity), self.name)
            
        for price_level, new_quantity in message["data"]['asks']: 
            price_level = float(price_level)
            self.asks[price_level] = (float(new_quantity), self.name)
            
    def _on_message(self, ws, message) -> None:  
        message = json.loads(message)
        if message["type"] == "partial":
            self._populate_orderbook(message)
            
        elif message["type"] == "update":
            self._update_orderbook(message)
        elif message["type"] == "subscribed":
            print("subscribe to goodalexhunting")
            return
        else: 
            return
        self.live.update(self._generate_table())
        
    def _on_open(self, ws) -> None:
        print("opening connection")
        ws.send(json.dumps({'op': 'subscribe', 'channel': 'orderbook', 'market': 'BTC/USDT'}))

def main() -> None:
    client: FtxOrderBook = FtxOrderBook()
    client.run()

if __name__ == "__main__":
    main()




    




