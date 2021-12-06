from typing import List
from .orderbook import OrderBook, Order


class OrderBooksManager:
    """
    Manages multiple order books, dumps and loads orders to disk,
    retrieves maximum prices and TWAMP
    """
    MAX_SIZE = 10000  # OrderBook maximum number of in-memory stored orders

    def add_order_book(self, orderbook: OrderBook) -> None:
        """Add order book to manager"""

    def dump_orders(self, orderbook: OrderBook, dump_path: str = None):
        """Dump order book orders to storage"""

    def load_orders(self, dump_path: str) -> List[Order]:
        """Load order book orders from storage"""
