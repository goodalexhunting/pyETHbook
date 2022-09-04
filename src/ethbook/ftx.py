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

# https://docs.ftx.com/#orderbooks

#TODO Checksum to make sure that our state is correct
#TODO Timestamp maybe

class FtxOrderBook():
    def __init__(self) -> FtxOrderBook:
        self.bids = SortedDict()
        self.asks = SortedDict()
        self.ws_url = f"wss://ftx.com/ws/"
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
        for price_level, new_quantity in message["data"]['bids']:
            price_level = float(price_level)
            self.bids[price_level] = float(new_quantity)
            if self.bids[price_level] == float(0):
                    self.bids.pop(price_level)

        for price_level, new_quantity in message["data"]['asks']:
            price_level = float(price_level)
            self.asks[price_level] = float(new_quantity)
            if self.asks[price_level] == float(0):
                self.asks.pop(price_level)
        
    def _populate_orderbook(self, message) -> None:
        for price_level, new_quantity in message["data"]['bids']:
            price_level = float(price_level)
            self.bids[price_level] = float(new_quantity)
            
        for price_level, new_quantity in message["data"]['asks']: 
            price_level = float(price_level)
            self.asks[price_level] = float(new_quantity)
            
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
    ftx_client: FtxOrderBook = FtxOrderBook()
    ftx_client.run()

if __name__ == "__main__":
    main()




    




