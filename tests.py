from dataclasses import dataclass
import heapq


@dataclass
class Order:
    uid: int
    price: float


class OrderBook:
    def __init__(self):
        self.init_timestamp = self.current_timestamp = 0
        self.twmp = 0.0
        self.removed = {}
        self.pq = []
        self.size = 0

    @property
    def twamp(self):
        """Get Time-Weighted Average Maximum Price"""
        return self.twmp / (self.current_timestamp - self.init_timestamp)

    @property
    def current_max_price(self) -> float:
        if not self.pq:
            return 0.0

        price, order_uid = self.pq[0] if self.pq else 0.0

        if order_uid in self.removed:
            price, order_uid = heapq.heappop(self.pq)
            del self.removed[order_uid]
            return self.current_max_price

        return -self.pq[0][0] if self.pq else 0.0

    def add(self, timestamp: int, order: Order):
        if not self.init_timestamp:
            self.init_timestamp = timestamp

        current_max = self.current_max_price

        if current_max != order.price:
            self.twmp += (timestamp - self.current_timestamp) * current_max
            self.current_timestamp = timestamp

        heapq.heappush(self.pq, (-order.price, order.uid))

    def remove(self, timestamp: int, order_id: int):
        current_max = self.current_max_price
        self.removed[order_id] = 1

        new_max = self.current_max_price

        if current_max != new_max:
            self.twmp += (timestamp - self.current_timestamp) * current_max
            self.current_timestamp = timestamp


def test_add_order_with_same_price():
    order_book = OrderBook()
    order_book.add(1000, Order(100, 10.0))
    order_book.add(2000, Order(101, 10.0))

    assert order_book.current_timestamp == order_book.init_timestamp == 1000
    assert order_book.current_max_price == 10.0


def test_add_order():
    order_book = OrderBook()
    order_book.add(1000, Order(100, 10.0))
    order_book.add(2000, Order(101, 11.0))

    assert order_book.current_timestamp == 2000
    assert order_book.current_max_price == 11.0


def test_delete_order():
    order_book = OrderBook()
    order_book.add(1000, Order(100, 10.0))
    order_book.add(1000, Order(101, 13.0))

    assert order_book.current_max_price == 13.0

    order_book.remove(2000, 101)
    assert order_book.current_max_price == 10.0


def test_twamp():
    order_book = OrderBook()
    order_book.add(1000, Order(100, 10.0))
    order_book.add(2000, Order(101, 13.0))
    order_book.add(2200, Order(102, 13.0))
    order_book.remove(2400, 101)
    order_book.remove(2500, 102)
    order_book.remove(4000, 100)

    assert order_book.twamp == 10.5


def test_twamp_1():
    order_book = OrderBook()
    order_book.add(1000, Order(100, 10.0))
    order_book.add(2000, Order(101, 13.0))
    order_book.add(2200, Order(102, 13.0))
    order_book.remove(2400, 102)
    order_book.remove(2500, 101)
    order_book.remove(4000, 100)

    assert order_book.twamp == 10.5