from websocket import WebSocketApp, enableTrace
import json
import requests
from sortedcontainers import SortedDict
from tabulate import tabulate
# https://binance-docs.github.io/apidocs/spot/en/#live-subscribing-unsubscribing-to-streams


def on_message(ws, message) -> None:
    print("received a message")

def on_open(ws, message) -> None:
    print("Opening conection")


def main() -> None:
    # enableTrace(True)
    # ws =  WebSocketApp("wss://api.gemini.com/v1/marketdata/BTCUSD", on_message=on_message, on_open=on_open)
    # ws.run_forever()

    ws2 =  WebSocketApp("wss://stream.binance.com:9443/ws/bnbbtc@depth20", on_message=on_message, on_open=on_open)
    # ws2.run_forever()
    bids: SortedDict = SortedDict()
    asks: SortedDict = SortedDict()
    orderbook = requests.get("https://api.binance.com/api/v3/depth?symbol=BNBBTC&limit=20").json()
    
    print(orderbook["lastUpdateId"])
    

    for price_level in orderbook["bids"]:
        bids[float(price_level[0])] = float(price_level[1])
    
    for price_level in orderbook["asks"]:
        asks[float(price_level[0])] = float(price_level[1])

    

    

    print(tabulate(bids.items()[:], headers=['Price', 'Quantity'], tablefmt='orgtbl'))
    


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
#   "b": [              // Bids to be updated
#     [
#       "0.0024",       // Price level to be updated
#       "10"            // Quantity
#     ]
#   ],
#   "a": [              // Asks to be updated
#     [
#       "0.0026",       // Price level to be updated
#       "100"           // Quantity
#     ]
#   ]
# }
    

if __name__ == "__main__":
    main()    


