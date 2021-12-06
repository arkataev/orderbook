import heapq
import os
import uuid
from typing import Iterator, List
import dataclasses
import enum

from order_book import Order

__all__ = ["parse_command", "CommandType"]


ROOT = os.path.dirname(__file__)
DUMP_PATH = os.path.join(ROOT, 'orders_dump')


class CommandType(enum.Enum):
    INSERT = "I"
    ERASE = "E"


@dataclasses.dataclass
class Command:
    timestamp: int
    command_type: CommandType
    order: Order

    def __post_init__(self):
        self.command_type = CommandType(self.command_type)


def parse_command(command_str: str) -> Command:
    """
    Parse string with order book command

    :param command_str: string with space separated 3-4 arguments (e.g. 1000 I 102 10.0)
    :raise ValueError: if could not parse command or invalid arguments provided
    """

    try:
        timestamp, _type, order_id, *price = command_str.strip("\n").split(sep=" ")
    except TypeError:
        raise ValueError(f'Invalid command string {command_str}')

    try:
        timestamp = int(timestamp)
    except ValueError:
        raise ValueError(f"Invalid timestamp {timestamp}")

    try:
        order_id = int(order_id)
    except ValueError:
        raise ValueError(f"Invalid order_id {order_id}")

    try:
        order_price = float(*price)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid order price {price}")

    return Command(timestamp=int(timestamp), command_type=_type, order=Order(order_id, order_price))


def merge_load_orders(*file_paths: str) -> Iterator[Order]:
    """Load and merge in sorted order multiple orders lists"""
    yield from heapq.merge(*(load_orders(path) for path in file_paths))


def dump_orders_desc(orders: List[Order], file_path: str = None) -> str:
    """Dump copy of orders list to disk in descending order. Order with maximum price is always first"""
    _file_path = file_path or str(uuid.uuid4())
    _orders = sorted(orders)

    with open(os.path.join(DUMP_PATH, _file_path), 'w') as f:
        f.writelines("\n".join(map(str, _orders)))

    return _file_path


def load_orders(file_path: str) -> Iterator[Order]:
    with open(os.path.join(DUMP_PATH, file_path), 'r') as f:

        for line in iter(f.readline, ""):
            uid, price = line.split(sep=" ")
            yield Order(int(uid), float(price))
