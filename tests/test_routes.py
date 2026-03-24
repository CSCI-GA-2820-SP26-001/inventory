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
TestYourResourceModel API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Inventory
from .factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

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


# ----------------------------------------------------------
# TEST LIST
# ----------------------------------------------------------
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
