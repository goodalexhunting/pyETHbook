from collections import defaultdict
class LimitLevel():
    def __init__(self):
        self.total_quantity : float = 0
        self.quantities = defaultdict(float)
    def update_quantity(self, exchange: str, new_quantity: float) -> None:
        previous_quantity = self.quantities[exchange]
        self.quantities[exchange] = new_quantity
        
        if new_quantity > previous_quantity:
            self.total_quantity = self.total_quantity + (new_quantity - previous_quantity)
        else:
            self.total_quantity = self.total_quantity - (previous_quantity - new_quantity)
            if not new_quantity:
                self.quantities.pop(exchange)
    



