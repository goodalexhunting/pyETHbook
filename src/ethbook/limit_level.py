from collections import defaultdict
class LimitLevel():
    def __init__(self):
        self.total_quantity : float = 0
        self._quantities = defaultdict(float)
    
    @property
    def quantities(self, exchange:str):
        return self._quantities[exchange]

    def update_quantity(self, exchange: str, new_quantity: float) -> None:
        previous_quantity = self._quantities[exchange]
        self._quantities[exchange] = new_quantity

        if new_quantity < previous_quantity:
            self.total_quantity = self.total_quantity - (previous_quantity - new_quantity)
        else:
            self.total_quantity = self.total_quantity + (new_quantity - previous_quantity)

        # self.total_quantity = self.total_quantity - (previous_quantity - new_quantity)
        # if self.total_quantity < 0:
        #     print(f"{previous_quantity=} {new_quantity=}")
        #     print(f"{self.total_quantity=}")

        
# limit_level = LimitLevel()
# limit_level.update_quantity('Binance', 0.22)
# print(limit_level.total_quantity)



