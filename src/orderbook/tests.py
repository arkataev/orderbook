from unittest import mock

import pytest

from order_book import Order, OrderBook, calculate_twp
from utils import parse_command


@pytest.fixture
def order_book() -> OrderBook:
    return OrderBook()


@pytest.mark.parametrize("time_start, time_end, max_price, expected", [
    (1, 2, 2, 2),
    (1, 2, 2.1, 2.1),
    (0, 1, 1, 1),
    (0, 1, 0, 0),
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
    assert not order_book.is_initiated()
    order_book.add(1, Order(1, 1))
    assert order_book.is_initiated()


def test_update_twmp(order_book):
    """
    When OrderBook time-weighted maximum price updated
    Then OrderBook twmp equals to existing twmp + new twmp
    """
    assert not order_book.twmp
    order_book._update_twmp(1, 2, 2)
    assert order_book.twmp == 2
    order_book._update_twmp(1, 2, 2)
    assert order_book.twmp == 4


def test_add_order_update_twmp(order_book):
    """
    Given Order
    And OrderBook current maximum price != Order price
    When Order added to OrderBook
    Then OrderBook twmp updated with OrderBook current maximum price and Order adding timestamp
    And OrderBook current timestamp == Order adding timestamp
    """
    order_book_current_max = order_book.get_max_price()
    timestamp = 1

    assert order_book.current_timestamp == 0

    with mock.patch('order_book.OrderBook._update_twmp') as update_twmp:
        order_book.add(timestamp, Order(1, 2))
        update_twmp.assert_called_with(0, timestamp, order_book_current_max)

    assert order_book.current_timestamp == timestamp


def test_add_order_with_same_price_not_update_twmp(order_book):
    """
    Given Order
    And OrderBook current maximum price == Order price
    When Order added to OrderBook
    Then OrderBook twmp is NOT updated
    And OrderBook current timestamp is NOT changed
    """
    assert order_book.current_timestamp == order_book.twmp == 0

    with mock.patch('order_book.OrderBook._update_twmp') as update_twmp:
        order_book.add(1, Order(1, 0))
        update_twmp.assert_not_called()

    assert order_book.current_timestamp == 0


def test_remove_order_update_twmp(order_book):
    """
    Given OrderBook has only one order with current maximum price
    When Order with current maximum price removed from OrderBook
    Then OrderBook twmp updated with OrderBook current maximum price and Order removing timestamp
    And OrderBook current timestamp == Order removing timestamp
    """
    timestamp = 1
    order = Order(1, 1)

    order_book.add(timestamp, order)
    order_book_current_max = order_book.get_max_price()

    with mock.patch('order_book.OrderBook._update_twmp') as update_twmp:
        order_book.remove(2, 1)
        update_twmp.assert_called_with(timestamp, 2, order_book_current_max)

    assert order_book.current_timestamp != timestamp


def test_remove_order_same_price_not_update_twmp(order_book):
    """
    Given OrderBook has only one order with current maximum price
    When Order with current maximum price removed from OrderBook
    Then OrderBook twmp updated with OrderBook current maximum price and Order removing timestamp
    And OrderBook current timestamp == Order removing timestamp
    """
    timestamp = 1
    order_1 = Order(1, 1)
    order_2 = Order(2, 1)

    order_book.add(timestamp, order_1)
    order_book.add(timestamp, order_2)

    with mock.patch('order_book.OrderBook._update_twmp') as update_twmp:
        order_book.remove(2, 1)
        update_twmp.assert_not_called()

    assert order_book.current_timestamp == timestamp


def test_get_max_price_empty(order_book):
    """
    Given OrderBook is empty
    When maximum price is calculated
    Then maximum price == 0.0
    """
    assert order_book.is_empty()
    assert not order_book.get_max_price()


def test_get_max_price(order_book):
    """
    Given Orderbook is not empty
    When maximum price is calculated
    Then maximum price is the highest price of all non-removed orders
    """
    order_book.add(1, Order(1, 1.0))
    order_book.add(2, Order(1, 2.0))
    assert order_book.get_max_price() == 2.0


def test_get_max_price_add(order_book):
    """
    Given Orderbook is not empty
    When new order added
    Then maximum price is the highest price of all non-removed orders
    """
    order_book.add(1, Order(1, 1.0))
    assert order_book.get_max_price() == 1.0
    order_book.add(2, Order(2, 2.0))
    assert order_book.get_max_price() == 2.0


def test_get_max_price_removed(order_book):
    """
    Given Orderbook is not empty
    When new order added
    Then maximum price is the highest price of all non-removed orders
    """
    order_book.add(1, Order(1, 1.0))
    order_book.add(2, Order(2, 2.0))
    assert order_book.get_max_price() == 2.0
    order_book.remove(3, 2)
    assert order_book.get_max_price() == 1.0
    order_book.remove(4, 1)
    assert order_book.get_max_price() == 0.0


@pytest.mark.parametrize('timestamp_orders, twamp', [
    ([(10, Order(1, 10.0)), (15, Order(2, 15.0)), (20, Order(3, 20.0))],
     ((15 - 10) * 10 + (20 - 15) * 15) / (20 - 10)),
])
def test_twamp_add(order_book, timestamp_orders, twamp):
    for timestamp, order in timestamp_orders:
        order_book.add(timestamp, order)
    assert order_book.twamp == twamp


@pytest.mark.parametrize('removed_orders, twamp', [
    ([(25, 1), (30, 2), (35, 3)], ((15 - 10) * 10 + (20 - 15) * 15 + (35 - 20) * 20) / (35 - 10)),
    ([(25, 3), (30, 2), (35, 1)],
     ((15 - 10) * 10 + (20 - 15) * 15 + (25 - 20) * 20 + (30 - 25) * 15 + (35 - 30) * 10) / (35 - 10)),
    ([(25, 2), (30, 3), (35, 1)],
     ((15 - 10) * 10 + (20 - 15) * 15 + (30 - 20) * 20 + (35 - 30) * 10) / (35 - 10)),
])
def test_twamp_remove(order_book, removed_orders, twamp):

    added_orders = [(10, Order(1, 10.0)), (15, Order(2, 15.0)), (20, Order(3, 20.0))]

    for timestamp, order in added_orders:
        order_book.add(timestamp, order)

    for timestamp, order in removed_orders:
        order_book.remove(timestamp, order)

    assert order_book.twamp == twamp


def test_default_scenario(order_book):
    order_book.add(1000, Order(100, 10.0))
    order_book.add(2000, Order(101, 13.0))
    order_book.add(2200, Order(102, 13.0))
    order_book.remove(2400, 101)
    order_book.remove(2500, 102)
    order_book.remove(4000, 100)

    assert order_book.twamp == 10.5


@pytest.mark.parametrize("command_string", ["abc I 1 1", "1000 R 1 1", "1000 E abc 1", "1000 E 1 abc"])
def test_parse_command_error(command_string):
    with pytest.raises(ValueError):
        parse_command(command_string)


@pytest.mark.parametrize("max_orders", [10, 100, 1000, 10000, 100000, 1000000])
def test_orderbook_load(order_book, max_orders):
    import random

    orders = [Order(i, float(random.randint(1, 100))) for i in range(1, max_orders)]
    sorted_orders = sorted(orders)

    for timestamp, order in zip(range(1, len(orders)), orders):
        order_book.add(timestamp, order)

    assert order_book.get_max_price() == sorted_orders[0].price
