Feature: Calculate Time-Weighted Average Maximum Price of orders

  Scenario: Adding Order
    Given Order does not exist
    When provided operation type is 'I' (insert order)
    Then New order with given ID and price is added
    And current maximum price is calculated

  Scenario: Erasing Order
    Given Order with provided ID exists
    When provided operation type is 'E' (erase order)
    Then Order with given ID and price is removed
    And current maximum price is calculated

  Scenario: Get current order maximum price
    Given

  Scenario: Calculate Time-Weighted Maximum Price
    Given at least one order exists
    When added order price != current maximum price
    Then time weighted maximum price is calculated

  Scenario: Calculate Time-Weighted Average Maximum Price
    Given a list of orders
    When all orders processed
    Then time weighted average maximum price returned to user