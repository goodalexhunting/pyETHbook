from __future__ import annotations
from ethbook.exchanges import OrderbookEvent, PriceUpdate
from ethbook.limit_level import LimitLevel
from sortedcontainers import SortedDict
from rich.live import Live
from rich.table import Table
from exchanges import FtxOrderBook, BinanceOrderBook
from colours import EXCHANGE_COLOURS
#  ,KrakenOrderBook, CoinbaseOrderBook, BinanceOrderBook
import multiprocessing as mp
from multiprocessing.heap import Heap

class CombinedBook:
    def __init__(self) -> None:
        self.bids: SortedDict[float, LimitLevel] = SortedDict()
        self.asks: SortedDict[float, LimitLevel] = SortedDict()
        self.live = Live()
        self.event_queue = mp.Queue()
        # exchanges = [BinanceOrderBook, CoinbaseOrderBook, KrakenOrderBook, FtxOrderBook]
        exchanges = [FtxOrderBook, BinanceOrderBook]
        self.exchanges = [cls(self.event_queue) for cls in exchanges]
    # TODO: #Use heap data structure instead of q and fetch 
    def run(self) -> None:

        for exchange in self.exchanges:
            job = mp.Process(
                target=exchange.run, daemon=True, name=exchange._NAME
            )
            job.start()
        self.live.start()
        while True:

            event = self.event_queue.get(block=True)
            # print(event)
            self._process_event(event)
            self.live.update(self._generate_table())

    # TODO: Try using a default callable for sorted dict --> self.bids.setdefault()
    def _update_side(
        self,
        side: SortedDict[float, LimitLevel],
        updates: list[PriceUpdate],
        name: str,
    ) -> None:
        for price, quantity in updates:
            if price in side:
                side[price].update_quantity(name, quantity)
            else:
                side[price] = LimitLevel.from_price_update(name, quantity)
            if -0.00000000001 < side[price].total_quantity < 0.00000000001:
                side.pop(price)

    def _process_event(self, event: OrderbookEvent) -> None:
        self._update_side(self.bids, event.bids, event.exchange_name)
        self._update_side(self.asks, event.asks, event.exchange_name)


    def _generate_table(self) -> Table:
        table = Table()
        columns = ('Price', 'Quantity', 'Exchange')
        for col in columns * 2:
            table.add_column(col)

        for ((bid_price, bid_level), (ask_price, ask_level)) in zip(
            reversed(self.bids.items()), self.asks.items()
        ):
            bid_exchanges = ''
            for exchange in bid_level.quantities.keys():
                bid_exchanges += f'[{EXCHANGE_COLOURS[exchange]}]{exchange} '
            ask_exchanges = ''
            for exchange in ask_level.quantities.keys():
                ask_exchanges += f'[{EXCHANGE_COLOURS[exchange]}]{exchange} '
            table.add_row(
                f'[green]{bid_price:}',
                f'[green]{bid_level.total_quantity:.3f}',
                f'{bid_exchanges}',
                f'[red]{ask_price:}',
                f'[red]{ask_level.total_quantity:.3f}',
                f'{ask_exchanges}',
            )
        return table


def main() -> None:
    combined_book: CombinedBook = CombinedBook()
    combined_book.run()


if __name__ == '__main__':
    main()
