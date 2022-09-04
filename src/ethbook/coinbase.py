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

class CoinbaseOrderBook():
    def __init__(self) -> CoinbaseOrderBook:
        self.bids = SortedDict()
        self.asks = SortedDict()
        self.ws_url = f"wss://ws-feed.exchange.coinbase.com"
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




    




