from __future__ import annotations
from ethbook.order_book import OrderBook
from websocket import WebSocketApp
import json
from sortedcontainers import SortedDict
from constants import PAIR1, PAIR2
from limit_level import LimitLevel
from rich.live import Live
import multiprocessing as mp

# https://docs.cloud.coinbase.com/exchange/docs/websocket-overview
# TODO Checksum to make sure that our state is correct
# TODO Timestamp maybe
class KrakenOrderBook(OrderBook):
    _WS_URL = f'wss://ws.kraken.com'
    _COLOUR = '#4c00b0'
    _NAME = 'Kraken'

    def __init__(
        self, bids: SortedDict, asks: SortedDict, live: Live
    ) -> None:
        super().__init__(bids, asks, live)
        self.name = 'kraken'
        self.timestamp = None

    def run(self) -> None:
        ws = WebSocketApp(
            self._WS_URL,
            on_message=self._wrap_callback(self._on_message),
            on_open=self._wrap_callback(self._on_open),
        )
        ws.run_forever()

    def _update_orderbook(self, message) -> None:
        try:
            self.process_orderbook_event(message['b'], self.bids)
        except KeyError:
            pass
        try:
            self.process_orderbook_event(message['a'], self.asks)
        except KeyError:
            pass

    def process_orderbook_event(
        self, orderbook_data: dict[str, list[str]], book_side: SortedDict
    ) -> None:
        for price_level, new_quantity, *_ in orderbook_data:
            price_level, new_quantity = float(price_level), float(new_quantity)
            try:
                book_side[price_level].update_quantity(
                    self._NAME, new_quantity
                )
            except KeyError:
                book_side[price_level] = LimitLevel()
                book_side[price_level].update_quantity(
                    self._NAME, new_quantity
                )
            if (
                -0.000000000001
                < book_side[price_level].total_quantity
                < 0.000000000001
            ):
                book_side.pop(price_level)

    def _populate_orderbook(self, message) -> None:
        self.process_orderbook_event(message['bs'], self.bids)
        self.process_orderbook_event(message['as'], self.asks)

    def _on_message(self, ws, message) -> None:
        message = json.loads(message)
        print('received message from kraken')
        if type(message) == list:
            try:
                message[1]['bs']
                self._populate_orderbook(message[1])
            except KeyError:
                self._update_orderbook(message[1])
        print(self._NAME)
        # self.live.update(self._generate_table())
        # self.group_by_price(self.bids)
        # self.group_by_price(self.ask)

    def _on_open(self, ws) -> None:
        print('opening connection')
        ws.send(
            json.dumps(
                {
                    'event': 'subscribe',
                    'pair': [f'{PAIR1}/{PAIR2}'],
                    'subscription': {'name': 'book'},
                }
            )
        )


def main() -> None:
    client: KrakenOrderBook = KrakenOrderBook()
    client.run()


if __name__ == '__main__':
    main()
