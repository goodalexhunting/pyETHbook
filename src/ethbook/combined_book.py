from __future__ import annotations
from ethbook.binance import BinanceOrderBook
from ethbook.coinbase import CoinbaseOrderBook
from ethbook.ftx import FtxOrderBook
from ethbook.kraken import KrakenOrderBook
import rel
from sortedcontainers import SortedDict
from rich.live import Live

class CombinedBook():
    def __init__(self) -> CombinedBook:
        self.bids = SortedDict()
        self.asks = SortedDict()
        self.live = Live()
        # orderbooks = [BinanceOrderBook, CoinbaseOrderBook, KrakenOrderBook, FtxOrderBook]
        orderbooks = [FtxOrderBook, KrakenOrderBook]
        # orderbooks = [CoinbaseOrderBook]
        self.orderbooks = list(map(lambda cls: cls(self.bids, self.asks, self.live), orderbooks))
        
    def run(self) -> None:
        self.live.start()
        for orderbook in self.orderbooks:
            orderbook.run()
        rel.signal(2, rel.abort)
        rel.dispatch()

def main() -> None:
    combined_book: CombinedBook = CombinedBook()
    combined_book.run()

if __name__ == "__main__":
    main()
