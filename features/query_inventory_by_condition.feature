Feature: Query Inventory by condition from UI
  As a store manager
  I need to filter inventory by condition from the UI
  So that I can quickly find matching items

  Background:
    Given the inventory service is running
    And the database is empty

  Scenario: Condition field is separate from ID lookup and query returns only matches
    Given the following inventory items exist
      | name      | condition | quantity |
      | Widget A  | new       | 10       |
      | Widget B  | used      | 4        |
      | Widget C  | new       | 7        |
    When I visit the inventory UI page
    Then I should see a separate condition query field
    When I query inventory by condition "new"
    Then only items with condition "new" are returned

  Scenario: Friendly message when condition query has no matches
    Given the following inventory items exist
      | name      | condition | quantity |
      | Widget X  | used      | 2        |
    When I query inventory by condition "open_box"
    Then no inventory items should be returned for the query
    And a friendly no-match query message is available
