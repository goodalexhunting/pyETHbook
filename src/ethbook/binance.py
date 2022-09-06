from __future__ import annotations
from threading import Thread
from ethbook.order_book import OrderBook
from websocket import WebSocketApp, enableTrace
import json
import requests
from sortedcontainers import SortedDict
from rich.live import Live
import rel
from limit_level import LimitLevel
from constants import PAIR1, PAIR2
# https://binance-docs.github.io/apidocs/spot/en/#live-subscribing-unsubscribing-to-streams

class BinanceOrderBook(OrderBook):
    
    _ORDERBOOK_URL = f"https://api.binance.com/api/v3/depth?symbol={PAIR1}{PAIR2}&limit=1000"
    _WS_URL = f"wss://stream.binance.com:9443/ws/ethusdt@depth"
    _COLOUR = "#F3BA2F"
    _NAME = "Binance"
    
    
    def __init__(self, bids: SortedDict, asks: SortedDict, live: Live) -> BinanceOrderBook:
        super().__init__(bids, asks, live)
        self.last_update_id = None 
        self.previous_update_id = 0

    def run(self) -> None:
        orderbook = requests.get(self._ORDERBOOK_URL).json()
        
        self.process_orderbook_event(orderbook["bids"], self.bids)
        self.process_orderbook_event(orderbook["asks"], self.asks)
        self.last_update_id = orderbook["lastUpdateId"]
        ws = WebSocketApp(self._WS_URL, on_message=self._wrap_callback(self._on_message), on_open=self._wrap_callback(self._on_message))
        ws.run_forever(dispatcher=rel)
    
    def process_orderbook_event(self, orderbook_data: list[list[str]], side: SortedDict[float, LimitLevel]) -> None:
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


    def _on_message(self, ws: WebSocketApp, message) -> None:
        message = json.loads(message)
        #print("received message")
        if int(message['u']) <= self.last_update_id:
            return
        self.process_orderbook_event(message['b'], self.bids)
        self.process_orderbook_event(message['a'], self.asks)

        self.live.update(self._generate_table())
        # print(F"BEST TEMP BID: {max(self.temp_bids.keys())} QTY: {self.temp_bids[max(self.temp_bids.keys())]}  BEST TEMP ASK: {min(self.temp_asks.keys())} QTY: {self.temp_asks[min(self.temp_asks.keys())]}")
        # print(F"BEST BID: {max(self.bids.keys())} QTY: {self.bids[max(self.bids.keys())].total_quantity} BEST ASK: {min(self.asks.keys())} QTY: {self.asks[min(self.asks.keys())].total_quantity}")
        self.previous_update_id = int(message['u'])
    
    def _on_open(self, ws, message) -> None:
        pass

def main() -> None:
    client: BinanceOrderBook = BinanceOrderBook()
    client.run()

if __name__ == "__main__":
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
    




