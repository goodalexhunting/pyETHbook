from rich.table import Table

from textual import events
from textual.app import App
from textual.widgets import ScrollView

import random
import time

from rich.live import Live
from rich.table import Table


def generate_table() -> Table:
    """Make a new table."""
    table = Table()
    table.add_column("Price")
    table.add_column("Quantity")
    # table.add_column("PriceLevel")
    # table.add_column("Quantity")


    

    price = 120
    quantity = 10

    for row in range(20):
        value = random.random() * 100
        table.add_row(
            f"[green]{price}", f"[green]{value}"
        )

        # "[red]ERROR" if value < 50 else "[green]SUCCESS"
    return table


with Live(generate_table(), refresh_per_second=4) as live:
    for _ in range(40):
        time.sleep(0.4)
        live.update(generate_table())
        