from __future__ import annotations
from websocket import WebSocketApp, enableTrace
import json
import requests
from sortedcontainers import SortedDict
from tabulate import tabulate
# https://binance-docs.github.io/apidocs/spot/en/#live-subscribing-unsubscribing-to-streams


class BinanceOrderBook():
    
    def __init__(self, limit = 20, delay = '1000ms') -> BinanceOrderBook:
        self.bids = SortedDict()
        self.asks = SortedDict()
        self.last_update_id:int = None 
        self.pair = "btcusdt"
        self.orderbook_url = f"https://api.binance.com/api/v3/depth?symbol={self.pair.upper()}&limit={limit}"
        self.ws_url = f"wss://stream.binance.com:9443/ws/{self.pair}@depth{limit}@{delay}"
    
    def _wrap_callback(self,f):
        def wrapped_f(ws, *args, **kwargs):
            try:
                f(ws, *args, **kwargs)
            except Exception as e:
                raise Exception(f"Error running websocket callback: {e}")
            
        return wrapped_f


    def _on_message(self, ws, message) -> None:
        print("received new message")
        message = json.loads(message)

        if message['lastUpdateId'] < self.last_update_id:
            print(f"{message['lastUpdateId']=} {self.last_update_id=}")
            return
        # print(message["bids"])

        for price_level, new_quantity in message['bids']:
            #print("iterating loop1")
            price_level = float(price_level)

            self.bids[price_level] = float(new_quantity)
            if self.bids[price_level] == float(0):
                print(f"PRICE LEVEL DELETED: {price_level}")
                self.bids.pop(price_level)

        for price_level, new_quantity in message['asks']:
            #print("iterating loop2")
            
            price_level = float(price_level)
            self.asks[price_level] = float(new_quantity)
            if self.asks[price_level] == float(0):
                print(f"PRICE LEVEL DELETED: {price_level}")
                self.asks.pop(price_level)
        
        self.last_update_id = message['lastUpdateId']
        
        table_1 = tabulate(self.bids.items()[:5], headers=['Price', 'Quantity'], tablefmt='orgtbl')
        table_2 = tabulate(self.asks.items()[:5], headers=['Price', 'Quantity'], tablefmt='orgtbl')

        print(f"{table_1}{table_2}")

    def _on_open(self, ws, message) -> None:
        print("Opening conection")


    def run(self) -> None:

        orderbook = requests.get(self.orderbook_url).json()
        
        print("Orderbook fetched")

        for price_level in orderbook["bids"]:
            self.bids[float(price_level[0])] = float(price_level[1])
        
        for price_level in orderbook["asks"]:
            self.asks[float(price_level[0])] = float(price_level[1])
        self.last_update_id = orderbook["lastUpdateId"]
        print("Orderbook populated")
        ws2 = WebSocketApp(self.ws_url, on_message=self._wrap_callback(self._on_message), on_open=self._wrap_callback(self._on_message))
        ws2.run_forever()


def main() -> None:
    binance_client: BinanceOrderBook = BinanceOrderBook()
    binance_client.run()


if __name__ == "__main__":
    main()

#TODO
#1) get current state of orderbook, and store it in two sorted containers
#2) listen to stream
#3) for each depthUpdate, update orderbook
#4) 

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
    




