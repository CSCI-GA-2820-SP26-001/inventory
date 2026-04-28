"""
TestInventoryService API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, InventoryItem, Condition
from .factories import InventoryItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventoryService(TestCase):
    """REST API Server Tests"""

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
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

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
