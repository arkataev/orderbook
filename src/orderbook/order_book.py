import heapq

from typing import List

__all__ = ["Order", "OrderBook", "calculate_twp"]


class Order:
    """Comparable Order to use in OrderBook. Orders compared by price"""

    __slots__ = ('uid', '_price')

    def __init__(self, uid: int, price: float):
        if price < 0:
            raise ValueError('Price must be positive number')
        self.uid = uid
        self._price = -price  # Invert price to use in min-heap as it was a max-heap

    @property
    def price(self):
        # Not to confuse price usage, this should be reversed back to positive value
        return -self._price

    def __lt__(self, other: "Order"):
        return self.price > other.price

    def __eq__(self, other: "Order"):
        return self.price == other.price

    def __str__(self):
        return f"{self.uid} {self.price}"


class OrderBook:
    """
    Collection of Orders with fast calculation of
    Time-Weighted Average Maximum Price of all containing Orders and
    retrieving current maximum price.

        Example:
            order_book = OrderBook()
            order_book.add(1000, Order(1, 10.0)
            order_book.add(2000, Order(2, 11.0)

            order_book.get_max_price()  # get current maximum price
            order_book.twamp            # get Time-Weighted Average Maximum Price
    """

    def __init__(self):
        self.twmp = 0.0
        self._init_timestamp = self._current_timestamp = 0
        self._removed_orders = set()
        # TODO:: This can potentially overgrow memory limit, as a solution we can dump orders to disk
        self._pq: List[Order] = []

    @property
    def current_timestamp(self) -> int:
        """OrderBook current timestamp"""
        return self._current_timestamp

    @property
    def twamp(self) -> float:
        """Get Time-Weighted Average Maximum Price"""
        return self.twmp / (self.current_timestamp - self._init_timestamp)

    def is_empty(self) -> bool:
        """Are there any Orders in OrderBook?"""
        return not self._pq

    def is_initiated(self) -> bool:
        """Were there any Orders in OrderBook?"""
        return self._init_timestamp > 0

    def get_max_price(self) -> float:
        """Get current overall maximum price of all non-deleted Orders in OrderBook"""

        # Speed-up resolving attributes in a loop
        pq, removed_orders = self._pq, self._removed_orders
        heappop, remove_order = heapq.heappop, removed_orders.remove

        while pq:
            order = pq[0]
            uid = order.uid

            if uid in removed_orders:
                # if order was removed we can ignore as it is no longer the maximum price order
                heappop(pq)
                remove_order(uid)
            else:
                # Found order that is not removed and is new maximum price order
                break
        else:
            # all orders were removed or not yet added
            return 0.0

        return order.price

    def add(self, timestamp: int, order: Order) -> None:
        """
        Add order from OrderBook and update time-weighted maximum average price
        if current maximum price differs from that before adding

        :param timestamp: Order adding timestamp
        :param order: Order to add
        """
        if not self._init_timestamp:
            self._init_timestamp = timestamp

        current_max_price = self.get_max_price()
        heapq.heappush(self._pq, order)

        if current_max_price != self.get_max_price():
            self._update_twmp(self.current_timestamp, timestamp, current_max_price)
            self._current_timestamp = timestamp

        return None

    def remove(self, timestamp: int, order_id: int) -> None:
        """
        Remove Order from OrderBook and update time-weighted maximum average price
        if current maximum price differs from that before removing

        :param timestamp: timestamp when Order was removed
        :param order_id: Order uid to remove from OrderBook
        """
        current_max_price = self.get_max_price()
        self._removed_orders.add(order_id)

        if current_max_price != self.get_max_price():
            self._update_twmp(self.current_timestamp, timestamp, current_max_price)
            self._current_timestamp = timestamp

        return None

    def _update_twmp(self, time_start: int, time_end: int, max_price: float) -> None:
        self.twmp += calculate_twp(time_start, time_end, max_price)
        return None


def calculate_twp(time_start: int, time_end: int, price: float) -> float:
    """Calculate Time-Weighted Price"""
    if time_start >= time_end:
        raise ValueError('End time should be greater then start time')
    elif price < 0:
        raise ValueError("Price must be positive number")
    return (time_end - time_start) * price
