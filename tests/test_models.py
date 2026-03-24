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

"""Test cases for Inventory Model"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Inventory, DataValidationError, db
from .factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Inventory   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestInventoryModel(TestCase):
    """Test Cases for Inventory Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_inventory(self):
        """It should create an Inventory"""
        inventory = InventoryFactory()
        inventory.create()
        self.assertIsNotNone(inventory.id)
        found = Inventory.all()
        self.assertEqual(len(found), 1)
        data = Inventory.find(inventory.id)
        self.assertEqual(data.name, inventory.name)

    def test_serialize_inventory(self):
        """It should serialize an Inventory"""
        inventory = InventoryFactory()
        inventory.create()
        data = inventory.serialize()
        self.assertEqual(data["id"], inventory.id)
        self.assertEqual(data["name"], inventory.name)
        self.assertEqual(data["product_id"], inventory.product_id)
        self.assertEqual(data["quantity_on_hand"], inventory.quantity_on_hand)
        self.assertEqual(data["restock_level"], inventory.restock_level)
        self.assertEqual(data["condition"], inventory.condition.value)

    def test_deserialize_inventory(self):
        """It should deserialize an Inventory from POST-like payload"""
        inventory = Inventory()
        payload = {
            "name": "keyboard",
            "product_id": "sku-123",
            "quantity_on_hand": 8,
            "restock_level": 3,
            "condition": "new",
        }
        inventory.deserialize(payload)
        self.assertEqual(inventory.name, payload["name"])
        self.assertEqual(inventory.product_id, payload["product_id"])
        self.assertEqual(inventory.quantity_on_hand, payload["quantity_on_hand"])
        self.assertEqual(inventory.restock_level, payload["restock_level"])
        self.assertEqual(inventory.condition.value, payload["condition"])

    def test_deserialize_inventory_missing_field(self):
        """It should not deserialize an Inventory with missing fields"""
        inventory = Inventory()
        payload = {
            "name": "keyboard",
            "quantity_on_hand": 8,
            "restock_level": 3,
            "condition": "new",
        }
        self.assertRaises(DataValidationError, inventory.deserialize, payload)


def test_list_all_inventory(self):
    """It should List all Inventory items in the database"""
    items = Inventory.all()
    self.assertEqual(items, [])

    # Create 5 Inventory items
    for _ in range(5):
        item = InventoryFactory()
        item.create()

    # See if we get back 5 items
    items = Inventory.all()
    self.assertEqual(len(items), 5)
