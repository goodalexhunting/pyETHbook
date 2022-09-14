from __future__ import annotations
from exchanges.order_book import OrderBook, OrderbookEvent
from websocket import WebSocketApp
import json
from limit_level import LimitLevel
from constants import PAIR1, PAIR2
import multiprocessing as mp
from typing import Any
from sortedcontainers import SortedDict


# https://docs.ftx.com/#orderbooks

# TODO Checksum to make sure that our state is correct
# TODO Timestamp maybe


class FtxOrderBook(OrderBook):

    _WS_URL = f'wss://ftx.com/ws/'
    _COLOUR = '#11A9BC'
    _NAME = 'FTX'

    def __init__(self, queue: mp.Queue) -> None:
        super().__init__(queue, self._NAME)

    def run(self) -> None:
        ws = WebSocketApp(
            self._WS_URL,
            on_message=self._wrap_callback(self._on_message),
            on_open=self._wrap_callback(self._on_open),
        )
        ws.run_forever()

    def process_orderbook_event(
        self,
        orderbook_data: list[list[str]],
        side: SortedDict[float, LimitLevel],
    ) -> None:
        for price, quantity in orderbook_data:
            price = float(price)
            quantity = float(quantity)
            try:
                side[price].update_quantity(self._NAME, quantity)
            except KeyError:
                side[price] = LimitLevel()
                side[price].update_quantity(self._NAME, quantity)
            if -0.000000000001 < side[price].total_quantity < 0.000000000001:
                side.pop(price)

    def _process_message(self, message: dict[str, Any]) -> None:
        asks = [
            (float(price), float(quantity))
            for price, quantity in message['data']['asks']
        ]
        bids = [
            (float(price), float(quantity))
            for price, quantity in message['data']['bids']
        ]
        event = OrderbookEvent(self._NAME, asks, bids)
        self.event_queue.put(event)

    def _process_update(self, message):
        pass

    def _on_message(self, ws, message) -> None:
        message = json.loads(message)
        if message['type'] == 'update' or message['type'] == 'partial':
            self._process_message(message)
            # self.process_orderbook_event(message["data"]["bids"], self.bids)
            # self.process_orderbook_event(message["data"]["asks"], self.asks)
        elif message['type'] == 'subscribed':
            print('subscribe to goodalexhunting')
            return
        else:
            return
        # self.live.update(self._generate_table())
        # self.group_by_price(self.bids)

    def _on_open(self, ws) -> None:
        print('opening connection')
        ws.send(
            json.dumps(
                {
                    'op': 'subscribe',
                    'channel': 'orderbook',
                    'market': f'{PAIR1}/{PAIR2}',
                }
            )
        )


def main() -> None:
    client: FtxOrderBook = FtxOrderBook()
    client.run()


if __name__ == '__main__':
    main()
