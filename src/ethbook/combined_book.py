from __future__ import annotations
from ethbook.exchanges import OrderbookEvent, PriceUpdate
from ethbook.limit_level import LimitLevel
from sortedcontainers import SortedDict
from rich.live import Live
from rich.table import Table
from exchanges import FtxOrderBook
#  ,KrakenOrderBook, CoinbaseOrderBook, BinanceOrderBook
import multiprocessing as mp

class CombinedBook():
    def __init__(self) -> CombinedBook:
        self.bids: SortedDict[float, LimitLevel] = SortedDict()
        self.asks: SortedDict[float, LimitLevel] = SortedDict()
        self.live = Live()
        self.event_queue = mp.Queue()
        # exchanges = [BinanceOrderBook, CoinbaseOrderBook, KrakenOrderBook, FtxOrderBook]
        exchanges = [FtxOrderBook]
        self.exchanges = [cls(self.event_queue) for cls in exchanges]

    
    def run(self) -> None:
        
        for exchange in self.exchanges:
            print("starting jobs...")
            job = mp.Process(target=exchange.run, daemon=True)
            job.start()
        self.live.start()
        while True:
            event = self.event_queue.get(block=True)
            # print(event)
            self._process_event(event)
            self.live.update(self._generate_table()) 


        
    #TODO: Try using a default callable for sorted dict --> self.bids.setdefault()
    def _update_side(self, side: SortedDict[float, LimitLevel], updates: list[PriceUpdate], name: str) -> None:
        for price, quantity in updates:
            try:
                side[price].update_quantity(name, quantity)                
            except KeyError:
                side[price] = LimitLevel.from_price_update(name, quantity)

    def _process_event(self, event: OrderbookEvent) -> None:
        self._update_side(self.bids, event.bids, event.exchange_name)
        self._update_side(self.asks, event.asks, event.exchange_name)
        
        # for price, quantity in event.bids:
        #     try:
        #         self.bids[price].update_quantity(event.exchange_name, quantity)                
        #     except KeyError:
        #         self.bids[price] = LimitLevel.from_price_update(event.exchange_name, quantity)
            


    
    
        # self.live.start()
        # for orderbook in self.orderbooks:
        #     orderbook.run()
        # rel.signal(2, rel.abort)
        # rel.dispatch()
    def _generate_table(self) -> Table:
        table = Table()
        columns = ["Price", "Quantity", "Exchange"]
        for col in columns * 2:
            table.add_column(col)
            
        for ((bid_price, bid_level), (ask_price, ask_level)) in zip(reversed(self.bids.items()[:]), self.asks.items()[:]): 
            bid_exchanges = ""
            for exchange in bid_level.quantities.keys():
                bid_exchanges += f"{exchange}"
            ask_exchanges = ""
            for exchange in ask_level.quantities.keys():
                ask_exchanges += f"{exchange} "
            table.add_row(
            f"[green]{bid_price}", f"[green]{bid_level.total_quantity}",f"{bid_exchanges}",
            f"[red]{ask_price}",f"[red]{ask_level.total_quantity}", f"{ask_exchanges}"
            )
            # [{EXCHANGE_COLOURS[exchange]}]
        return table
        


def main() -> None:
    # print('hello noob')
    combined_book: CombinedBook = CombinedBook()
    combined_book.run()

if __name__ == "__main__":
    main()
