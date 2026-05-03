Feature: List All Inventory Items
  As a store manager
  I need to view all inventory items in the UI
  So that I can get a full view of current stock levels

  Background:
    Given the inventory service is running
    And the database is empty

  Scenario: List button is visible on the home page
    When I visit the home page
    Then I should see a "List All Inventory" button

  Scenario: Listing inventory when no items exist
    When I visit the home page
    And I click the "List All Inventory" button
    Then I should see the message "No inventory items found."
    And the inventory table should not be visible

  Scenario: Listing inventory with multiple items
    Given the following inventory items exist
      | name    | condition | quantity |
      | Widget  | new       | 10       |
      | Gadget  | used      | 5        |
      | Doohick | open_box  | 2        |
    When I visit the home page
    And I click the "List All Inventory" button
    Then I should see 3 items in the inventory table
    And the inventory table should be visible
    And I should see the item fields "ID", "Name", "Condition", "Quantity"

  Scenario: All item fields are shown in the table
    Given the following inventory items exist
      | name   | condition | quantity |
      | Widget | new       | 10       |
    When I visit the home page
    And I click the "List All Inventory" button
    Then I should see "Widget" in the inventory table
    And I should see "new" in the inventory table
    And I should see "10" in the inventory table

  Scenario: GET /api/inventory returns all items as JSON
    Given the following inventory items exist
      | name   | condition | quantity |
      | Widget | new       | 10       |
      | Gadget | used      | 5        |
    When I request "GET" "/api/inventory"
    Then the response status code should be 200
    And the response should be a JSON list of 2 items
    And each item should have fields "id", "name", "condition", "quantity"
