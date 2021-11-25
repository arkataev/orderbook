import heapq
import uuid
from typing import List, Iterator, Optional
import os

__all__ = ["Order", "OrderBook", "calculate_twp"]

ROOT = os.path.dirname(__file__)
DUMP_PATH = os.path.join(ROOT, 'orders_dump')


class Order:
    """Orderable Order to use in OrderBook"""

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
    MAX_SIZE = 100

    def __init__(self, orders_dump: Optional[str] = None):
        self.twmp = 0.0
        self._init_timestamp = self._current_timestamp = 0
        self._removed_orders = set()
        self._pq: List[Order] = []
        self._dumped_orders = orders_dump or []
        self._cached_max_price_order: Optional[Order] = None

    @property
    def current_timestamp(self) -> int:
        """OrderBook current timestamp"""
        return self._current_timestamp

    @property
    def twamp(self) -> float:
        """Get Time-Weighted Average Maximum Price"""
        return self.twmp / (self.current_timestamp - self._init_timestamp)

    def is_empty(self) -> bool:
        """Are there any Orders in OrderNook"""
        return not self._pq

    def is_initiated(self) -> bool:
        """Were there any Orders in OrderBook?"""
        return self._init_timestamp > 0

    def get_cached_max_price_order(self) -> Optional[Order]:
        dump_pq = filter(
            lambda o: o.uid not in self._removed_orders,
            heapq.merge(*(load_orders(path) for path in self._dumped_orders))
        )

        try:
            order = next(dump_pq)
        except StopIteration:
            order = None

        return order

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
            cached_order = self.get_cached_max_price_order()
            return cached_order.price if cached_order else 0.0

        cached_max_price_order = self.get_cached_max_price_order()

        if cached_max_price_order and cached_max_price_order.price > order.price:
            return cached_max_price_order.price

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

        if len(self._pq) >= self.MAX_SIZE:
            self._dumped_orders.append(dump_orders_sorted(self._pq))
            self._pq = []

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
        :return:
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


def dump_orders_sorted(orders: List[Order]) -> str:
    file_path = str(uuid.uuid4())
    orders.sort()
    with open(os.path.join(DUMP_PATH, file_path), 'w') as f:
        f.writelines("\n".join(map(str, orders)))

    return file_path


def load_orders(file_path: str) -> Iterator[Order]:
    with open(os.path.join(DUMP_PATH, file_path), 'r') as f:
        lines = iter(f.readline, "")
        for line in lines:
            uid, price = line.split(sep=" ")
            yield Order(int(uid), float(price))
