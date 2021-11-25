import dataclasses
import enum
import logging
import time
from argparse import ArgumentParser

from orderbook import OrderBook, Order

logging.basicConfig(format='%(message)s', level=logging.INFO)


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
    timestamp, _type, order_id, *price = command_str.strip("\n").split(sep=" ")
    return Command(timestamp=int(timestamp), command_type=_type, order=Order(int(order_id), float(*price)))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('file_path', type=str)
    ns = parser.parse_args()

    orderbook = OrderBook()

    with open(ns.file_path) as f:
        start = time.perf_counter()

        for line in f.readlines():
            command = parse_command(line)

            if command.command_type == CommandType.INSERT:
                orderbook.add(command.timestamp, command.order)
            elif command.command_type == CommandType.ERASE:
                orderbook.remove(command.timestamp, command.order.uid)

        end = time.perf_counter()

    logging.info(f"Time-Weighted Average Maximum Price: {orderbook.twamp} \nTime: {round(end - start, 5)} seconds")
