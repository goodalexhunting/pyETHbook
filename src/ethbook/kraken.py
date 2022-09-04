from __future__ import annotations
from threading import Thread
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

class KrakenOrderBook():
    def __init__(self) -> KrakenOrderBook:
        self.bids = SortedDict()
        self.asks = SortedDict()
        self.ws_url = f"wss://ws.kraken.com"
        self.timestamp = None

    def run(self) -> None:  
        ws = WebSocketApp(self.ws_url, on_message=self._wrap_callback(self._on_message), on_open=self._wrap_callback(self._on_open))
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
    
    def _update_orderbook(self, message) -> None:
        try:
            for price_level, new_quantity, *_ in message['b']:
                price_level = float(price_level)
                self.bids[price_level] = float(new_quantity)
                if self.bids[price_level] == float(0):
                        self.bids.pop(price_level)
        except KeyError:
            pass
        try:
            for price_level, new_quantity, *_ in message['a']:
                price_level = float(price_level)
                self.asks[price_level] = float(new_quantity)
                if self.asks[price_level] == float(0):
                    self.asks.pop(price_level)
        except KeyError:
            pass

    def _populate_orderbook(self, message) -> None:
        for price_level, new_quantity, _ in message['bs']:
            price_level = float(price_level)
            self.bids[price_level] = float(new_quantity)
            
        for price_level, new_quantity, _ in message['as']: 
            price_level = float(price_level)
            self.asks[price_level] = float(new_quantity)
            
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




    




