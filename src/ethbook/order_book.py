from abc import ABC, abstractmethod
from ethbook.colours import EXCHANGE_COLOURS
from rich.live import Live
from rich.table import Table
from sortedcontainers import SortedDict
from limit_level import LimitLevel
from typing import Iterable
from itertools import groupby
from functools import reduce

class OrderBook(ABC):
    def __init__(self, bids: SortedDict, asks: SortedDict, live: Live) -> None:
        self.bids = bids
        self.asks = asks
        self.live = live
        self.name = None
    @abstractmethod
    def run(self) -> None:
        pass
    
    def _wrap_callback(self,f):
        def wrapped_f(ws, *args, **kwargs):
            try:
                f(ws, *args, **kwargs)
            except Exception as e:
                raise Exception(f"Error running websocket callback: {e}")
        return wrapped_f
    
    def _generate_table(self) -> Table:
        table = Table()
        columns = ["Price", "Quantity", "Exchange"]
        for col in columns * 2:
            table.add_column(col)
            
        for ((bid_price, bid_level), (ask_price, ask_level)) in zip(reversed(self.bids.items()[:]), self.asks.items()[:]): 
            bid_exchanges = ""
            for exchange in bid_level.quantities.keys():
                bid_exchanges += f"[{EXCHANGE_COLOURS[exchange]}]{exchange} "
            ask_exchanges = ""
            for exchange in ask_level.quantities.keys():
                ask_exchanges += f"[{EXCHANGE_COLOURS[exchange]}]{exchange} "
            table.add_row(
            f"[green]{bid_price}", f"[green]{bid_level.total_quantity}",f"{bid_exchanges}",
            f"[red]{ask_price}",f"[red]{ask_level.total_quantity}", f"{ask_exchanges}"
            )
            
        return table
    
    def group_by_price(self, side: SortedDict[float, LimitLevel]) -> Iterable[tuple[int, float, str]]:
        print(self.name)
        return
        
        return_side = list(map(lambda x: (x[0], x[1].total_quantity, set(x[1].quantities.keys())), side.items()))
        print(return_side)
        grouped_side = map(lambda x: (x[0], list(x[1])),groupby(return_side, lambda x: int(x[0])))
        return_side = map(lambda x: (x[0], sum(qty for _, qty, _ in x[1]), " ".join(reduce(lambda x, y: x | y, (ex for *_, ex in x[1])))), grouped_side)
        print(list(return_side))
        #return return_side

    def _generate_collapsed_table(self) -> Table:
        table = Table()
        columns = ["Price", "Quantity", "Exchange"]
        for col in columns * 2:
            table.add_column(col)

        asks = list(self.group_by_price(self.asks))
        bids = reversed(list(self.group_by_price(self.bids)))
        
        
        for ((bid_price, bid_quantity, bid_exchanges), (ask_price, ask_quantity, ask_exchanges)) in zip(bids, asks):
            table.add_row(
            f"[green]{bid_price}", f"[green]{bid_quantity}",f"{bid_exchanges}",
            f"[red]{ask_price}",f"[red]{ask_quantity}", f"{ask_exchanges}"
            )
        return table
    