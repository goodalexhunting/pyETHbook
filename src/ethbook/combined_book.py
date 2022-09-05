from __future__ import annotations
from threading import Thread
from ethbook.binance import BinanceOrderBook
from ethbook.coinbase import CoinbaseOrderBook
from ethbook.ftx import FtxOrderBook
from ethbook.kraken import KrakenOrderBook
from websocket import WebSocketApp, enableTrace
import rel
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


class CombinedBook():
    def __init__(self) -> CombinedBook:
        self.bids = SortedDict()
        self.asks = SortedDict()
        self.live = Live()
        # orderbooks = [BinanceOrderBook, FtxOrderBook, CoinbaseOrderBook, KrakenOrderBook]
        orderbooks = [FtxOrderBook]
        self.orderbooks = list(map(lambda cls: cls(self.bids, self.asks, self.live), orderbooks))


    def run(self) -> None:
        self.live.start()
        for orderbook in self.orderbooks:
            orderbook.run()
        # map(lambda o: o.run(), self.orderbooks)
        rel.signal(2, rel.abort)
        rel.dispatch()

def main() -> None:
    combined_book: CombinedBook = CombinedBook()
    combined_book.run()


if __name__ == "__main__":
    main()
