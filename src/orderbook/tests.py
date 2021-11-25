from .orderbook import Order, OrderBook, calculate_twp
import pytest
from unittest import mock


@pytest.fixture
def order_book() -> OrderBook:
    return OrderBook()


@pytest.mark.parametrize("time_start, time_end, max_price, expected", [
    (1, 2, 2, 2),
    (1, 2, 2.1, 2.1),
    (0, 0, 1, 0),
    (0, 0, 0, 0),
])
def test_calculate_twmp(time_start, time_end, max_price, expected):
    assert calculate_twp(time_start, time_end, max_price) == expected


def test_order_book_init(order_book):
    """
    Given OrderBook is empty
    And initial timestamp is 0
    When order is added to OrderBook
    Then initial time stamp is equal to order adding timestamp
    """
    assert not order_book.init_timestamp
    order_book.add(1, Order(1,1))
    assert order_book.init_timestamp == 1


def test_update_twmp(order_book):
    """
    When OrderBook time-weighted maximum price updated
    Then OrderBook twmp equals to existing twmp + new twmp
    """
    assert not order_book.twmp
    order_book.update_twmp(1, 2, 2)
    assert order_book.twmp == 2
    order_book.update_twmp(1, 2, 2)
    assert order_book.twmp == 4


def test_add_order(order_book):
    """
    Given Order
    And OrderBook current maximum price != Order price
    When Order added to OrderBook
    Then OrderBook twmp updated with OrderBook current maximum price and Order adding timestamp
    And OrderBook current timestamp == Order adding timestamp
    """
    order_book_current_max = order_book.get_max_price()
    timestamp = 1

    assert order_book.current_timestamp == order_book.twmp == 0
    assert order_book_current_max == 0.0

    with mock.patch('orderbook.orderbook.OrderBook.update_twmp') as update_twmp:
        order_book.add(timestamp, Order(timestamp, 2))
        update_twmp.assert_called_with(0, timestamp, order_book_current_max)

    assert order_book.current_timestamp == timestamp


def test_add_order_with_same_price(order_book):
    """
    Given Order
    And OrderBook current maximum price == Order price
    When Order added to OrderBook
    Then OrderBook twmp is NOT updated
    And OrderBook current timestamp is NOT changed
    """
    order_book_current_max = order_book.get_max_price()
    timestamp = 1

    assert order_book.current_timestamp == order_book.twmp == 0
    assert order_book_current_max == 0.0

    with mock.patch('orderbook.orderbook.OrderBook.update_twmp') as update_twmp:
        order_book.add(timestamp, Order(timestamp, 0))
        update_twmp.assert_not_called()

    assert order_book.current_timestamp == 0

#
# def test_add_order():
#     order_book = OrderBook()
#     order_book.add(1000, Order(100, 10.0))
#     order_book.add(2000, Order(101, 11.0))
#
#     assert order_book.current_timestamp == 2000
#     assert order_book.get_max_price() == 11.0


def test_delete_order():
    order_book = OrderBook()
    order_book.add(1000, Order(100, 10.0))
    order_book.add(1000, Order(101, 13.0))

    assert order_book.get_max_price() == 13.0

    order_book.remove(2000, 101)
    assert order_book.get_max_price() == 10.0


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
