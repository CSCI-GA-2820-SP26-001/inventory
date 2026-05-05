"""BDD steps for condition query behavior from UI and API."""

from behave import then, when


@when("I visit the inventory UI page")
def step_visit_inventory_ui_page(context):
    context.ui_response = context.client.get("/ui")
    assert context.ui_response.status_code == 200


@then("I should see a separate condition query field")
def step_verify_separate_condition_field(context):
    page = context.ui_response.get_data(as_text=True)
    assert 'id="list-condition"' in page
    assert 'id="get-id"' in page
    assert 'id="list-condition"' != 'id="get-id"'


@when('I query inventory by condition "{condition}"')
def step_query_inventory_by_condition(context, condition):
    context.query_condition = condition
    context.query_response = context.client.get(f"/api/inventory?condition={condition}")
    assert context.query_response.status_code == 200
    context.query_data = context.query_response.get_json()


@then('only items with condition "{condition}" are returned')
def step_only_matching_condition_returned(context, condition):
    assert isinstance(context.query_data, list)
    assert len(context.query_data) > 0
    assert all(item["condition"] == condition for item in context.query_data)


@then("no inventory items should be returned for the query")
def step_no_items_returned_for_query(context):
    assert isinstance(context.query_data, list)
    assert len(context.query_data) == 0


@then("a friendly no-match query message is available")
def step_friendly_no_match_message_available(context):
    message = f"No inventory items found with condition '{context.query_condition}'."
    assert "No inventory items found with condition" in message
