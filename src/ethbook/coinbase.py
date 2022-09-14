from ethbook.order_book import OrderBook
from websocket import WebSocketApp, enableTrace, create_connection
import json
from sortedcontainers import SortedDict
from rich.live import Live
from constants import PAIR1, PAIR2
from limit_level import LimitLevel

# https://docs.cloud.coinbase.com/exchange/docs/websocket-overview

# TODO Checksum to make sure that our state is correct
# TODO Timestamp maybe


class CoinbaseOrderBook(OrderBook):
    _WS_URL = f'wss://ws-feed.exchange.coinbase.com'
    _COLOUR = '#1554f0'
    _NAME = 'Coinbase'

    def __init__(self, bids: SortedDict, asks: SortedDict, live: Live):
        super().__init__(bids, asks, live)
        self.timestamp = None

    def run(self) -> None:
        ws = WebSocketApp(
            self._WS_URL,
            on_message=self._wrap_callback(self._on_message),
            on_open=self._wrap_callback(self._on_open),
        )
        ws.run_forever()

    def _update_orderbook(self, message) -> None:
        for side, price_level, new_quantity in message['changes']:
            book_side = None
            price_level, new_quantity = float(price_level), float(new_quantity)
            if side == 'buy':
                book_side = self.bids
            else:
                book_side = self.asks
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

    def process_orderbook_event(
        self, orderbook_data: dict[str, list[str]], book_side: SortedDict
    ) -> None:
        for price_level, new_quantity in orderbook_data:
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

    def _populate_orderbook(self, message) -> None:
        self.process_orderbook_event(message['bids'], self.bids)
        self.process_orderbook_event(message['asks'], self.asks)

    def _on_message(self, ws, message) -> None:
        # print(message)
        message = json.loads(message)
        if message['type'] == 'snapshot':
            self._populate_orderbook(message)
        elif message['type'] == 'l2update':
            self._update_orderbook(message)
        elif message['type'] == 'subscribed':
            print('subscribe to goodalexhunting')
            return
        else:
            return
        print(self._NAME)

        # self.live.update(self._generate_table())

    def _on_open(self, ws) -> None:
        print('opening connection')
        ws.send(
            json.dumps(
                {
                    'type': 'subscribe',
                    'product_ids': [f'{PAIR1}-{PAIR2}'],
                    'channels': ['level2'],
                }
            )
        )


def main() -> None:
    client: CoinbaseOrderBook = CoinbaseOrderBook()
    client.run()


if __name__ == '__main__':
    main()
