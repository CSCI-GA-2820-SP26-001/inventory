"""
TestInventoryService API Service Test Suite
REST API tests for the Inventory service.
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, InventoryItem, Condition
from .factories import InventoryItemFactory
from service.models import ItemCondition, db, Inventory
from tests.factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/inventory"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventoryService(TestCase):
    """REST API Server Tests"""
# pylint: disable=too-many-public-methods
class TestInventoryService(TestCase):
    """REST API server tests for Inventory."""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(InventoryItem).delete()
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create inventory items
    ############################################################
    def _create_inventory_items(self, count: int = 1) -> list:
        """Factory method to create inventory items in bulk"""
        items = []
        for _ in range(count):
            test_item = InventoryFactory()
            response = self.client.post(BASE_URL, json=test_item.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test inventory item",
            )
            new_item = response.get_json()
            test_item.id = new_item["id"]
            items.append(test_item)
        return items

    ######################################################################
    #  I N D E X   T E S T S
    ######################################################################

    def test_index_returns_ui(self):
        """It should return the inventory management UI page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"Inventory Management", resp.data)

    def test_index_contains_list_button(self):
        """It should render a List All Inventory button on the index page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"list-btn", resp.data)
        self.assertIn(b"List All Inventory", resp.data)

    def test_index_contains_inventory_table(self):
        """It should render a table structure on the index page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"inventory-table", resp.data)
        self.assertIn(b"inventory-body", resp.data)

    def test_index_contains_empty_message_element(self):
        """It should render an empty state message element on the index page"""
    ######################################################################
    #  TEST FOR CREATE INVENTORY
    ######################################################################
    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"empty-message", resp.data)

    ######################################################################
    #  L I S T   I N V E N T O R Y   T E S T S
    ######################################################################

    def test_list_inventory_returns_empty_list(self):
        """
        GIVEN no inventory items exist
        WHEN I request GET /api/inventory
        THEN I should receive an empty list with status 200
        """
        resp = self.client.get("/api/inventory")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_list_inventory_returns_all_items(self):
        """
        GIVEN five inventory items exist in the database
        WHEN I request GET /api/inventory
        THEN I should receive all five items with status 200
        """
        for _ in range(5):
            item = InventoryItemFactory()
            item.create()
        resp = self.client.get("/api/inventory")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_list_inventory_item_has_required_fields(self):
        """
        GIVEN an inventory item exists
        WHEN I request GET /api/inventory
        THEN each item in the response should contain id, name, condition, and quantity
        """
        item = InventoryItemFactory(name="Widget", condition=Condition.NEW, quantity=10)
        item.create()
        resp = self.client.get("/api/inventory")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        result = data[0]
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertIn("condition", result)
        self.assertIn("quantity", result)

    def test_list_inventory_item_values_are_correct(self):
        """
        GIVEN a known inventory item exists
        WHEN I request GET /api/inventory
        THEN the returned item should match the stored values
        """
        item = InventoryItem(name="Sprocket", condition=Condition.USED, quantity=42)
        item.create()
        resp = self.client.get("/api/inventory")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        result = data[0]
        self.assertEqual(result["name"], "Sprocket")
        self.assertEqual(result["condition"], "used")
        self.assertEqual(result["quantity"], 42)
        self.assertEqual(result["id"], item.id)

    def test_list_inventory_returns_json_content_type(self):
        """
        GIVEN inventory items exist
        WHEN I request GET /api/inventory
        THEN the response content type should be application/json
        """
        InventoryItemFactory().create()
        resp = self.client.get("/api/inventory")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("application/json", resp.content_type)

    def test_list_inventory_with_multiple_conditions(self):
        """
        GIVEN items with different condition values exist
        WHEN I request GET /api/inventory
        THEN all items with their correct conditions should be returned
        """
        InventoryItem(name="New Widget", condition=Condition.NEW, quantity=5).create()
        InventoryItem(name="Used Widget", condition=Condition.USED, quantity=3).create()
        InventoryItem(name="Open Box Widget", condition=Condition.OPEN_BOX, quantity=1).create()

        resp = self.client.get("/api/inventory")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 3)

        conditions = {item["condition"] for item in data}
        self.assertIn("new", conditions)
        self.assertIn("used", conditions)
        self.assertIn("open_box", conditions)

    def test_list_inventory_single_item(self):
        """
        GIVEN exactly one inventory item exists
        WHEN I request GET /api/inventory
        THEN a list with exactly one item should be returned
        """
        item = InventoryItemFactory()
        item.create()
        resp = self.client.get("/api/inventory")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)

    def test_list_inventory_zero_quantity_item(self):
        """
        GIVEN an inventory item with zero quantity exists
        WHEN I request GET /api/inventory
        THEN the item should appear in the list with quantity 0
        """
        InventoryItem(name="Out of Stock", condition=Condition.NEW, quantity=0).create()
        resp = self.client.get("/api/inventory")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["quantity"], 0)
    def test_favicon(self):
        """It should return 204 for /favicon.ico"""
        resp = self.client.get("/favicon.ico")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_health(self):
        """It should return service health as JSON"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json(), {"status": "OK"})

    def test_inventory_ui_retrieve_controls(self):
        """It should provide retrieve-by-id controls in the UI."""
        resp = self.client.get("/ui")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        page = resp.get_data(as_text=True)
        self.assertIn('id="get-inventory-form"', page)
        self.assertIn('id="get-id" name="id" type="number" min="1" required', page)
        self.assertIn('id="retrieve-button" type="submit">Retrieve</button>', page)

    def test_inventory_ui_retrieve_wiring_and_not_found_message(self):
        """It should wire retrieve flow and show a clear not found message."""
        resp = self.client.get("/ui")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        page = resp.get_data(as_text=True)
        self.assertIn('getForm.addEventListener("submit"', page)
        self.assertIn('const data = await requestJson(`/inventory/${id}`, { method: "GET" });', page)
        self.assertIn('setSuccess("Inventory item retrieved successfully.", data);', page)
        self.assertIn('if (error.status === 404)', page)
        self.assertIn('setError(new Error("Inventory item not found."));', page)

    def test_inventory_ui_page(self):
        """It should serve the inventory admin UI with core operation controls."""
        resp = self.client.get("/ui")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        page = resp.get_data(as_text=True)
        self.assertIn("Inventory Admin", page)
        self.assertIn('id="create-inventory-form"', page)
        self.assertIn('id="get-inventory-form"', page)
        self.assertIn('id="update-inventory-form"', page)
        self.assertIn('id="delete-inventory-form"', page)
        self.assertIn('id="restock-inventory-form"', page)
        self.assertIn('id="list-inventory-form"', page)
        self.assertIn('id="message"', page)
        self.assertIn('id="result-display"', page)
        self.assertIn('fetch("/inventory"', page)

    def test_inventory_ui_create_flow_elements(self):
        """It should provide create flow inputs, request wiring, and result feedback."""
        resp = self.client.get("/ui")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        page = resp.get_data(as_text=True)

        # Required input fields for creating an item
        self.assertIn('id="create-name" name="name" type="text" required', page)
        self.assertIn(
            'id="create-product_id" name="product_id" type="text" required', page
        )
        self.assertIn(
            'id="create-quantity_on_hand" name="quantity_on_hand" type="number" min="0" required',
            page,
        )
        self.assertIn(
            'id="create-restock_level" name="restock_level" type="number" min="0" required',
            page,
        )
        self.assertIn('id="create-condition" name="condition" required', page)
        self.assertIn('id="create-button" type="submit">Create</button>', page)

        # Create request sent to backend
        self.assertIn('createForm.addEventListener("submit"', page)
        self.assertIn('const data = await requestJson("/inventory", {', page)
        self.assertIn('method: "POST"', page)
        self.assertIn('headers: { "Content-Type": "application/json" }', page)

        # Success and created item display
        self.assertIn('setSuccess("Inventory item created successfully.", data);', page)
        self.assertIn('id="message"', page)
        self.assertIn('id="result-display"', page)

    def test_create_inventory(self):
        """It should create a new Inventory record"""
        test_inventory = InventoryFactory()
        payload = {
            "name": test_inventory.name,
            "product_id": test_inventory.product_id,
            "quantity_on_hand": test_inventory.quantity_on_hand,
            "restock_level": test_inventory.restock_level,
            "condition": test_inventory.condition.value,
        }
        resp = self.client.post(
            "/inventory",
            json=payload,
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(resp.headers.get("Location"))

        new_inventory = resp.get_json()
        self.assertEqual(new_inventory["name"], payload["name"])
        self.assertEqual(new_inventory["product_id"], payload["product_id"])
        self.assertEqual(new_inventory["quantity_on_hand"], payload["quantity_on_hand"])
        self.assertEqual(new_inventory["restock_level"], payload["restock_level"])
        self.assertEqual(new_inventory["condition"], payload["condition"])
        self.assertIn("id", new_inventory)

    def test_create_inventory_no_data(self):
        """It should not create an Inventory record with missing body"""
        resp = self.client.post(
            "/inventory",
            data="",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inventory_no_content_type(self):
        """It should not create an Inventory record with wrong content type"""
        resp = self.client.post(
            "/inventory",
            data="some data",
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_inventory_bad_data(self):
        """It should not create an Inventory record with invalid data"""
        resp = self.client.post(
            "/inventory",
            json={"bad_field": "bad_value"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    ######################################################################
    #  TEST FOR GET INVENTORY
    ######################################################################
    def test_get_inventory(self):
        """It should get an existing Inventory record"""
        inventory = InventoryFactory()
        inventory.create()

        resp = self.client.get(f"/inventory/{inventory.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["id"], inventory.id)
        self.assertEqual(data["name"], inventory.name)
        self.assertEqual(data["product_id"], inventory.product_id)
        self.assertEqual(data["quantity_on_hand"], inventory.quantity_on_hand)
        self.assertEqual(data["restock_level"], inventory.restock_level)
        self.assertEqual(data["condition"], inventory.condition.value)

    def test_get_inventory_not_found(self):
        """It should return 404 for an Inventory record that does not exist"""
        resp = self.client.get("/inventory/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_inventory(self):
        """It should update an existing Inventory record (PUT)"""
        inventory = InventoryFactory()
        inventory.create()
        payload = {
            "name": "updated-name",
            "product_id": "SKU-UPDATED",
            "quantity_on_hand": 99,
            "restock_level": 5,
            "condition": "used",
        }
        resp = self.client.put(
            f"/inventory/{inventory.id}",
            json=payload,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], inventory.id)
        self.assertEqual(data["name"], payload["name"])
        self.assertEqual(data["product_id"], payload["product_id"])
        self.assertEqual(data["quantity_on_hand"], payload["quantity_on_hand"])
        self.assertEqual(data["restock_level"], payload["restock_level"])
        self.assertEqual(data["condition"], payload["condition"])

    def test_update_inventory_not_found(self):
        """It should return 404 when updating a missing inventory id"""
        resp = self.client.put(
            "/inventory/999999",
            json={
                "name": "x",
                "product_id": "y",
                "quantity_on_hand": 1,
                "restock_level": 1,
                "condition": "new",
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_inventory_no_content_type(self):
        """It should return 415 when PUT body is not application/json"""
        inventory = InventoryFactory()
        inventory.create()
        resp = self.client.put(
            f"/inventory/{inventory.id}",
            data="{}",
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_inventory_no_data(self):
        """It should return 400 when PUT body is empty or invalid JSON"""
        inventory = InventoryFactory()
        inventory.create()
        resp = self.client.put(
            f"/inventory/{inventory.id}",
            data="",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_inventory(self):
        """It should delete an inventory item and return 204"""
        items = self._create_inventory_items(1)
        iid = items[0].id
        resp = self.client.delete(f"/inventory/{iid}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        resp_get = self.client.get(f"/inventory/{iid}")
        self.assertEqual(resp_get.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_inventory_not_found(self):
        """It should return 204 when deleting a missing inventory id"""
        resp = self.client.delete("/inventory/999999")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_inventory(self):
        """It should list all Inventory items"""
        self._create_inventory_items(3)

        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)

    def test_list_inventory_empty(self):
        """It should return an empty list when there are no inventory items"""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    ######################################################################
    # TEST QUERY INVENTORY BY CONDITION
    ######################################################################
    def test_query_inventory_by_condition(self):
        """It should Query Inventory items by condition"""
        item1 = InventoryFactory(condition=ItemCondition.NEW)
        response = self.client.post(BASE_URL, json=item1.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        item2 = InventoryFactory(condition=ItemCondition.NEW)
        response = self.client.post(BASE_URL, json=item2.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        item3 = InventoryFactory(condition=ItemCondition.USED)
        response = self.client.post(BASE_URL, json=item3.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(f"{BASE_URL}?condition=new")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(len(data), 2)
        for item in data:
            self.assertEqual(item["condition"], "new")

    def test_query_inventory_by_condition_no_matches(self):
        """It should return an empty list when no Inventory items match the condition"""
        item = InventoryFactory(condition=ItemCondition.USED)
        response = self.client.post(BASE_URL, json=item.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(f"{BASE_URL}?condition=new")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(data, [])

    def test_query_inventory_by_bad_condition(self):
        """It should return 400 for an invalid condition query"""
        response = self.client.get(f"{BASE_URL}?condition=invalid")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_inventory_low_stock_true(self):
        """GET /inventory?low_stock=true returns rows with qty <= restock_level"""
        low1 = InventoryFactory(quantity_on_hand=2, restock_level=5)
        low1.create()
        low2 = InventoryFactory(quantity_on_hand=10, restock_level=10)
        low2.create()
        ok = InventoryFactory(quantity_on_hand=50, restock_level=5)
        ok.create()

        response = self.client.get(f"{BASE_URL}?low_stock=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        ids = {row["id"] for row in data}
        self.assertSetEqual(ids, {low1.id, low2.id})
        for row in data:
            self.assertLessEqual(row["quantity_on_hand"], row["restock_level"])

    def test_list_inventory_low_stock_true_case_insensitive(self):
        """low_stock accepts TRUE (case-insensitive)"""
        InventoryFactory(quantity_on_hand=1, restock_level=10).create()

        response = self.client.get(f"{BASE_URL}?low_stock=TRUE")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.get_json()), 1)

    def test_list_inventory_low_stock_no_matches(self):
        """low_stock returns empty list when every item is above restock level"""
        InventoryFactory(quantity_on_hand=100, restock_level=5).create()

        response = self.client.get(f"{BASE_URL}?low_stock=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.is_json)
        self.assertEqual(response.get_json(), [])

    def test_list_inventory_low_stock_false_lists_all(self):
        """low_stock=false does not apply the filter (returns full list)"""
        InventoryFactory(quantity_on_hand=100, restock_level=5).create()

        response = self.client.get(f"{BASE_URL}?low_stock=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.get_json()), 1)

    def test_list_inventory_filter_by_product_id(self):
        """GET inventory list with product_id returns matching rows (200, JSON)"""
        sku = "SKU-TRACK-XYZ"
        a = InventoryFactory(product_id=sku)
        a.create()
        b = InventoryFactory(product_id=sku)
        b.create()
        InventoryFactory(product_id="OTHER-SKU").create()

        response = self.client.get(f"{BASE_URL}?product_id={sku}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        for row in data:
            self.assertEqual(row["product_id"], sku)

    def test_list_inventory_filter_product_id_no_matches(self):
        """List filter by product_id returns empty list when nothing matches"""
        InventoryFactory(product_id="ONLY-THIS").create()

        response = self.client.get(f"{BASE_URL}?product_id=NONEXISTENT")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_list_inventory_filter_product_id_strips_whitespace(self):
        """List filter trims whitespace on the product_id query parameter"""
        sku = "SKU-TRIM"
        InventoryFactory(product_id=sku).create()

        response = self.client.get(f"{BASE_URL}?product_id=%20{sku}%20")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_id"], sku)

    def test_api_list_inventory(self):
        """It should list inventory using /api/inventory route."""
        self._create_inventory_items(2)
        response = self.client.get("/api/inventory")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.is_json)
        self.assertEqual(len(response.get_json()), 2)

    def test_api_inventory_item_crud(self):
        """It should support item CRUD via /api/inventory/<id> routes."""
        created = InventoryFactory()
        create_resp = self.client.post("/api/inventory", json=created.serialize())
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        item_id = create_resp.get_json()["id"]

        get_resp = self.client.get(f"/api/inventory/{item_id}")
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(get_resp.get_json()["id"], item_id)

        update_payload = {
            "name": "api-updated",
            "product_id": "API-SKU-1",
            "quantity_on_hand": 12,
            "restock_level": 3,
            "condition": "open_box",
        }
        update_resp = self.client.put(f"/api/inventory/{item_id}", json=update_payload)
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(update_resp.get_json()["name"], update_payload["name"])

        delete_resp = self.client.delete(f"/api/inventory/{item_id}")
        self.assertEqual(delete_resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_api_restock_inventory(self):
        """It should restock an item using /api/inventory/<id>/restock."""
        inventory = InventoryFactory(quantity_on_hand=2, restock_level=1)
        inventory.create()
        response = self.client.put(
            f"/api/inventory/{inventory.id}/restock",
            json={"amount": 5},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["quantity_on_hand"], 7)
