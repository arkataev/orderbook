import logging
import sys
import time
from argparse import ArgumentParser

from .orderbook import OrderBook
from .utils import parse_command, CommandType

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO, stream=sys.stderr)

parser = ArgumentParser()
parser.add_argument('file_path', type=str)
ns = parser.parse_args()
orderbook = OrderBook()


try:
    with open(ns.file_path) as f:
        start = time.perf_counter()

        for line in f.readlines():
            try:
                command = parse_command(line)
            except ValueError as e:
                logging.error(e)
                exit(1)

            try:
                if command.command_type == CommandType.INSERT:
                    orderbook.add(command.timestamp, command.order)
                elif command.command_type == CommandType.ERASE:
                    orderbook.remove(command.timestamp, command.order.uid)
            except ValueError as e:
                logging.error(e)
                exit(1)

        end = time.perf_counter()
except FileNotFoundError as e:
    logging.error(e)
    exit(1)

logging.info(f"Time-Weighted Average Maximum Price: {orderbook.twamp} \nTime: {round(end - start, 5)} seconds")
