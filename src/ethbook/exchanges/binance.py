from __future__ import annotations
from exchanges.order_book import OrderBook, OrderbookEvent
from websocket import WebSocketApp
import json
from constants import PAIR1, PAIR2
import multiprocessing as mp
import requests
from typing import Any
# https://binance-docs.github.io/apidocs/spot/en/#live-subscribing-unsubscribing-to-streams

class BinanceOrderBook(OrderBook):

    _ORDERBOOK_URL = f'https://api.binance.com/api/v3/depth?symbol={PAIR1}{PAIR2}&limit=1000'
    _WS_URL = f'wss://stream.binance.com:9443/ws/ethusdt@depth'
    _COLOUR = '#F3BA2F'
    _NAME = 'Binance'

    def __init__(
        self, queue: mp.Queue
    ) -> None:
        super().__init__(queue, self._NAME)
        self.last_update_id = None
        self.previous_update_id = 0

    def run(self) -> None:
        response = requests.get(self._ORDERBOOK_URL).json()
        self._process_snapshot(response)
        self.last_update_id = response['lastUpdateId']
        ws = WebSocketApp(
            self._WS_URL,
            on_message=self._wrap_callback(self._on_message),
        )
        ws.run_forever()

    def _process_snapshot(self, message: dict[str, Any]) -> None:
        self._submit_event(message['asks'], message['bids'])            

    def _submit_event(self, asks: list[list[str]], bids: list[list[str]]) -> None:
        
        asks = [
            (float(price), float(quantity))
            for price, quantity in asks
        ]
        
        bids = [
            (float(price), float(quantity))
            for price, quantity in bids
        ]
        
        event = OrderbookEvent(self._NAME, asks, bids)
        self.event_queue.put(event)
        
    def _process_update(self, message: str) -> None:
        message = json.loads(message)
        if int(message['u']) <= self.last_update_id:
            return
        self._submit_event(message['a'], message['b'])            
        self.previous_update_id = int(message['u'])
        
    def _on_message(self, ws: WebSocketApp, message) -> None:
        self._process_update(message)
        
    def _on_open(self, ws, message) -> None:
        raise NotImplementedError()


def main() -> None:
    client: BinanceOrderBook = BinanceOrderBook()
    client.run()


if __name__ == '__main__':
    main()


# "https://api.binance.com/api/v3/depth/exchangeInfo?symbol=BNBBTC"
# {
#   "e": "depthUpdate", // Event type
#   "E": 123456789,     // Event time
#   "s": "BNBBTC",      // Symbol
#   "U": 157,           // First update ID in event
#   "u": 160,           // Final update ID in event
#   "b": [              // seBids to be updated
#     [
#       "0.0024",       // Price level to be updated
#       "10"            // Quantity
#     ]
#   ],
#   "a": [              // self.Asks to be updated
#     [
#       "0.0026",       // Price level to be updated
#       "100"           // Quantity
#     ]
#   ]
# }
