######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
REST API tests for the Inventory service.
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import ItemCondition, db, Inventory
from tests.factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/inventory"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestInventoryService(TestCase):
    """REST API server tests for Inventory."""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
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
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    ######################################################################
    #  TEST FOR CREATE INVENTORY
    ######################################################################
    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_favicon(self):
        """It should return 204 for /favicon.ico"""
        resp = self.client.get("/favicon.ico")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_health(self):
        """It should return service health as JSON"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json(), {"status": "OK"})

    def test_inventory_ui_page(self):
        """It should serve the inventory UI with a create form."""
        resp = self.client.get("/ui")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        page = resp.get_data(as_text=True)
        self.assertIn("Create Inventory Item", page)
        self.assertIn('id="create-inventory-form"', page)
        self.assertIn('fetch("/inventory"', page)

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
