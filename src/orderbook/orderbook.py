import heapq


class Order:
    __slots__ = ('uid', '_price')

    def __init__(self, uid: int, price: float):
        self.uid = uid
        self._price = -price  # Invert price to use in min-heap as it was a max-heap

    @property
    def price(self):
        # Not to confuse price usage, this should be reversed back to positive value
        return -self._price

    def __lt__(self, other: "Order"):
        return self.price > other.price


class OrderBook:
    def __init__(self):
        self.init_timestamp = self.current_timestamp = 0
        self.twmp = 0.0
        self.removed_orders = set()
        self.pq = []

    @property
    def twamp(self) -> float:
        """Get Time-Weighted Average Maximum Price"""
        return self.twmp / (self.current_timestamp - self.init_timestamp)

    def get_max_price(self) -> float:
        """

        :return:
        """
        # Speed-up resolving attributes in a loop
        pq, removed_orders = self.pq, self.removed_orders
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

        :param timestamp:
        :param order:
        :return:
        """
        if not self.init_timestamp:
            self.init_timestamp = timestamp

        current_max_price = self.get_max_price()

        if current_max_price != order.price:
            self.update_twmp(self.current_timestamp, timestamp, current_max_price)
            self.current_timestamp = timestamp

        heapq.heappush(self.pq, order)
        return None

    def remove(self, timestamp: int, order_id: int) -> None:
        """

        :param timestamp:
        :param order_id: order uid to remove from OrderBook
        :return:
        """
        current_max_price = self.get_max_price()
        self.removed_orders.add(order_id)

        if current_max_price != self.get_max_price():
            self.update_twmp(self.current_timestamp, timestamp, current_max_price)
            self.current_timestamp = timestamp

        return None

    def update_twmp(self, time_start: int, time_end: int, max_price: float) -> None:
        self.twmp += calculate_twp(time_start, time_end, max_price)
        return None


def calculate_twp(time_start: int, time_end: int, price: float) -> float:
    """Calculate Time-Weighted  Price"""
    if time_start > time_end:
        raise ValueError('End time should be greater then start time')
    elif price < 0:
        raise ValueError("Price can't be negative")
    return (time_end - time_start) * price
