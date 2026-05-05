Feature: UI smoke test
  As a developer
  I need a minimal Selenium smoke test
  So that we can verify the UI workflow harness is wired correctly

  Scenario: Selenium framework is configured
    Given Selenium dependencies are available
    Then the webdriver options should be configured for headless runs

  Scenario: Inventory UI home page loads (smoke)
    When I open the inventory UI smoke endpoint
    Then I should see the inventory admin heading
