"""
BDD Steps for List All Inventory feature
"""

from behave import given, when, then
from service.models import Inventory, ItemCondition, db

CONDITION_MAP = {
    "new": ItemCondition.NEW,
    "used": ItemCondition.USED,
    "open_box": ItemCondition.OPEN_BOX,
}


@given("the inventory service is running")
def step_service_is_running(context):
    assert context.client is not None


@given("the database is empty")
def step_database_is_empty(context):
    db.session.query(Inventory).delete()
    db.session.commit()


@given("the following inventory items exist")
def step_inventory_items_exist(context):
    for row in context.table:
        item = Inventory(
            name=row["name"],
            product_id=f"BDD-{row['name']}",
            condition=CONDITION_MAP[row["condition"]],
            quantity_on_hand=int(row["quantity"]),
            restock_level=1,
        )
        item.create()


@when('I visit the home page')
def step_visit_home_page(context):
    context.response = context.client.get("/")
    assert context.response.status_code == 200


@when('I click the "List All Inventory" button')
def step_click_list_button(context):
    context.api_response = context.client.get("/api/inventory")


@when('I request "{method}" "{url}"')
def step_api_request(context, method, url):
    context.api_response = context.client.open(url, method=method)


@then('I should see a "List All Inventory" button')
def step_see_list_button(context):
    assert b"List All Inventory" in context.response.data
    assert b"list-btn" in context.response.data


@then('I should see the message "No inventory items found."')
def step_see_empty_message(context):
    data = context.api_response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0


@then("the inventory table should not be visible")
def step_table_not_visible(context):
    data = context.api_response.get_json()
    assert len(data) == 0


@then("the inventory table should be visible")
def step_table_is_visible(context):
    data = context.api_response.get_json()
    assert len(data) > 0


@then("I should see {count:d} items in the inventory table")
def step_see_n_items(context, count):
    data = context.api_response.get_json()
    assert len(data) == count


@then('I should see the item fields "{f1}", "{f2}", "{f3}", "{f4}"')
def step_see_item_fields(context, f1, f2, f3, f4):
    data = context.api_response.get_json()
    assert len(data) > 0
    item = data[0]
    for field in [f1.lower(), f2.lower(), f3.lower(), f4.lower()]:
        assert field in item, f"Field '{field}' not found in item"


@then('I should see "{value}" in the inventory table')
def step_see_value_in_table(context, value):
    data = context.api_response.get_json()
    assert len(data) > 0
    found = any(
        str(v) == value
        for item in data
        for v in item.values()
    )
    assert found, f"Value '{value}' not found in inventory response"


@then("the response status code should be {code:d}")
def step_response_status(context, code):
    assert context.api_response.status_code == code


@then("the response should be a JSON list of {count:d} items")
def step_response_json_list(context, count):
    data = context.api_response.get_json()
    assert isinstance(data, list)
    assert len(data) == count


@then('each item should have fields "{f1}", "{f2}", "{f3}", "{f4}"')
def step_each_item_has_fields(context, f1, f2, f3, f4):
    data = context.api_response.get_json()
    for item in data:
        for field in [f1, f2, f3, f4]:
            assert field in item, f"Field '{field}' missing from item {item}"
