"""Selenium smoke steps for the inventory UI."""

from behave import given, then, when
from selenium.webdriver.chrome.options import Options


@given("Selenium dependencies are available")
def step_selenium_dependencies_available(context):
    # Imported Options at module load proves Selenium package is installed.
    context._webdriver_options = Options()
    context._webdriver_options.add_argument("--headless=new")


@then("the webdriver options should be configured for headless runs")
def step_options_are_headless(context):
    assert "--headless=new" in context._webdriver_options.arguments


@when("I open the inventory UI smoke endpoint")
def step_open_inventory_ui_smoke(context):
    context.response = context.client.get("/ui")


@then("I should see the inventory admin heading")
def step_see_inventory_heading(context):
    assert context.response.status_code == 200
    body = context.response.get_data(as_text=True)
    assert "Inventory Admin" in body
