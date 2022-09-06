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

class KrakenOrderBook(OrderBook):
    def __init__(self, combined_bids: SortedDict, combined_asks: SortedDict, live: Live) -> KrakenOrderBook:
        super().__init__(combined_bids, combined_asks, live)
        self.name = "Kraken"
        self.ws_url = f"wss://ws.kraken.com"
        self.timestamp = None
        self.exchange_colour = "#4c00b0"

    def run(self) -> None:  
        ws = WebSocketApp(self.ws_url, on_message=self._wrap_callback(self._on_message), on_open=self._wrap_callback(self._on_open))
        self.live = Live(self._generate_table())
        self.live.start()
        ws.run_forever()

    def _update_orderbook(self, message) -> None:
        try:
            for price_level, new_quantity, *_ in message['b']:
                price_level = float(price_level)
                self.bids[price_level] = (float(new_quantity), self.name)
                if self.bids[price_level] == float(0):
                        self.bids.pop(price_level)
        except KeyError:
            pass
        try:
            for price_level, new_quantity, *_ in message['a']:
                price_level = float(price_level)
                self.asks[price_level] = (float(new_quantity), self.name)
                if self.asks[price_level] == float(0):
                    self.asks.pop(price_level)
        except KeyError:
            pass

    def _populate_orderbook(self, message) -> None:
        for price_level, new_quantity, _ in message['bs']:
            price_level = float(price_level)
            self.bids[price_level] = (float(new_quantity), self.name)
            
        for price_level, new_quantity, _ in message['as']: 
            price_level = float(price_level)
            self.asks[price_level] = (float(new_quantity), self.name)
            
    def _on_message(self, ws, message) -> None:  
        message = json.loads(message)
        if type(message) == list:
            try:
                message[1]['bs']
                self._populate_orderbook(message[1])
            except KeyError:
                self._update_orderbook(message[1])

        self.live.update(self._generate_table())
        
    def _on_open(self, ws) -> None:
        print("opening connection")
        ws.send(json.dumps({
        "event": "subscribe",
        "pair": [
            "BTC/USDT"],
        "subscription": {
            "name": "book"}
            }))

def main() -> None:
    client: KrakenOrderBook = KrakenOrderBook()
    client.run()

if __name__ == "__main__":
    main()




    




