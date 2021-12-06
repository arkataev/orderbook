import heapq
import os
import uuid
from typing import Iterator, List

from .orderbook import Order

ROOT = os.path.dirname(__file__)
DUMP_PATH = os.path.join(ROOT, 'orders_dump')


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
