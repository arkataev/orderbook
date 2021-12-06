# Task
A program for offline analyzing a set of tagged data containing two types of messages:
* Adding an order (with its price)
* Deleting previously added order

The program should implement the OrderBook class, which maintains a list of current orders that have been added 
but not deleted yet. It should also be possible to request the current maximum price of the order at any time. 
You must use this class in a program that reads the input file and displays the time-weighted average highest price of 
orders at the end. 
Complexity and memory consumption are very important.


## Conditions
The program must take one parameter - the name of the input file. Input file format:

Each line contains 3 or 4 fields, separated by spaces: 
1. Timestamp operation (integer, milliseconds from the beginning of the receipt of orders)
2. Type of operation (one character, I - insert order, E - erase order)
3. Identifier (32-bit integer)
4. Order price (real, double precision) (Note: this field is only present for insert order messages)

* Timestamp monotonously increasing
* There may be periods when there are no orders (in this case, such periods should not be considered)
* Each identifier appears exactly two times: one when inserted, the second when erased
* Deleting an order always goes after adding it.

### Run Example
```bash
python3 src/orderbook example.txt
```