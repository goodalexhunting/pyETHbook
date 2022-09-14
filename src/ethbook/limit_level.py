from __future__ import annotations
from collections import defaultdict


class LimitLevel:
    def __init__(self):
        self.total_quantity: float = 0
        self.quantities = defaultdict(float)

    @classmethod
    def from_price_update(cls, exchange: str, quantity: float) -> LimitLevel:
        limit_level = LimitLevel()
        limit_level.quantities[exchange] = quantity
        limit_level.total_quantity += quantity
        return limit_level

    def update_quantity(self, exchange: str, new_quantity: float) -> None:
        previous_quantity = self.quantities[exchange]
        self.quantities[exchange] = new_quantity

        if new_quantity > previous_quantity:
            self.total_quantity = self.total_quantity + (
                new_quantity - previous_quantity
            )
        else:
            self.total_quantity = self.total_quantity - (
                previous_quantity - new_quantity
            )
            if not new_quantity:
                self.quantities.pop(exchange)
