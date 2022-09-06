from abc import ABC, abstractmethod
from rich.live import Live
from rich.table import Table
from sortedcontainers import SortedDict
from limit_level import LimitLevel
class OrderBook(ABC):

    def __init__(self, bids: SortedDict, asks: SortedDict, live: Live) -> None:
        self.bids = bids
        self.asks = asks
        self.live = live
        self.exchange_colour = None

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
        table.add_column("Price")
        table.add_column("Quantity")
        table.add_column("Price")
        table.add_column("Quantity")
        for ((bid_price, bid_level), (ask_price, ask_level)) in zip(reversed(self.bids.items()[:]), self.asks.items()[:]): 
            table.add_row(
            f"[green]{bid_price}", f"[green]{bid_level.total_quantity}",
            f"[red]{ask_price}",f"[red]{ask_level.total_quantity}"
            )
            # f"[{self.exchange_colour}]{ask_exchange}"
        return table
    