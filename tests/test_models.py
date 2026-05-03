"""
Test cases for InventoryItem Model
"""
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

import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import InventoryItem, Condition, DataValidationError, db
from .factories import InventoryItemFactory
from service.models import Inventory, DataValidationError, ItemCondition, db
from .factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  I N V E N T O R Y   I T E M   M O D E L   T E S T   C A S E S
######################################################################
class TestInventoryItemModel(TestCase):
    """Test Cases for InventoryItem Model"""
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
        db.session.query(InventoryItem).delete()
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_inventory_item(self):
        """It should create an InventoryItem and assert that it exists"""
        item = InventoryItem(name="Widget", condition=Condition.NEW, quantity=10)
        self.assertIsNotNone(item)
        self.assertIsNone(item.id)
        self.assertEqual(item.name, "Widget")
        self.assertEqual(item.condition, Condition.NEW)
        self.assertEqual(item.quantity, 10)

    def test_add_inventory_item(self):
        """It should create an InventoryItem and add it to the database"""
        items = InventoryItem.all()
        self.assertEqual(items, [])
        item = InventoryItemFactory()
        item.create()
        self.assertIsNotNone(item.id)
        items = InventoryItem.all()
        self.assertEqual(len(items), 1)

    def test_read_inventory_item(self):
        """It should read an InventoryItem from the database"""
        item = InventoryItemFactory()
        item.create()
        found = InventoryItem.find(item.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, item.id)
        self.assertEqual(found.name, item.name)
        self.assertEqual(found.condition, item.condition)
        self.assertEqual(found.quantity, item.quantity)

    def test_update_inventory_item(self):
        """It should update an InventoryItem in the database"""
        item = InventoryItemFactory()
        item.create()
        original_id = item.id
        item.name = "Updated Widget"
        item.quantity = 99
        item.update()
        found = InventoryItem.find(original_id)
        self.assertEqual(found.name, "Updated Widget")
        self.assertEqual(found.quantity, 99)

    def test_update_without_id_raises_error(self):
        """It should raise DataValidationError when updating an item with no ID"""
        item = InventoryItemFactory()
        item.id = None
        self.assertRaises(DataValidationError, item.update)

    def test_delete_inventory_item(self):
        """It should delete an InventoryItem from the database"""
        item = InventoryItemFactory()
        item.create()
        self.assertEqual(len(InventoryItem.all()), 1)
        item.delete()
        self.assertEqual(len(InventoryItem.all()), 0)

    def test_serialize_inventory_item(self):
        """It should serialize an InventoryItem to a dictionary"""
        item = InventoryItem(name="Gadget", condition=Condition.USED, quantity=5)
        item.create()
        data = item.serialize()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "Gadget")
        self.assertEqual(data["condition"], "used")
        self.assertEqual(data["quantity"], 5)

    def test_deserialize_inventory_item(self):
        """It should deserialize an InventoryItem from a dictionary"""
        data = {"name": "Thingamajig", "condition": "open_box", "quantity": 3}
        item = InventoryItem()
        item.deserialize(data)
        self.assertEqual(item.name, "Thingamajig")
        self.assertEqual(item.condition, Condition.OPEN_BOX)
        self.assertEqual(item.quantity, 3)

    def test_deserialize_missing_name(self):
        """It should raise DataValidationError when name is missing"""
        data = {"condition": "new", "quantity": 1}
        item = InventoryItem()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_missing_condition(self):
        """It should raise DataValidationError when condition is missing"""
        data = {"name": "Widget", "quantity": 1}
        item = InventoryItem()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_missing_quantity(self):
        """It should raise DataValidationError when quantity is missing"""
        data = {"name": "Widget", "condition": "new"}
        item = InventoryItem()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_invalid_condition(self):
        """It should raise DataValidationError for an invalid condition value"""
        data = {"name": "Widget", "condition": "broken", "quantity": 1}
        item = InventoryItem()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_bad_data_type(self):
        """It should raise DataValidationError when data is not a dict"""
        item = InventoryItem()
        self.assertRaises(DataValidationError, item.deserialize, None)

    def test_all_returns_all_items(self):
        """It should return all InventoryItems in the database"""
        for _ in range(5):
            item = InventoryItemFactory()
            item.create()
        items = InventoryItem.all()
        self.assertEqual(len(items), 5)

    def test_find_by_name(self):
        """It should find InventoryItems by name"""
        item1 = InventoryItemFactory(name="Apple")
        item1.create()
        item2 = InventoryItemFactory(name="Apple")
        item2.create()
        item3 = InventoryItemFactory(name="Banana")
        item3.create()
        found = list(InventoryItem.find_by_name("Apple"))
        self.assertEqual(len(found), 2)

    def test_find_by_condition(self):
        """It should find InventoryItems by condition"""
        item1 = InventoryItemFactory(condition=Condition.NEW)
        item1.create()
        item2 = InventoryItemFactory(condition=Condition.NEW)
        item2.create()
        item3 = InventoryItemFactory(condition=Condition.USED)
        item3.create()
        found = list(InventoryItem.find_by_condition(Condition.NEW))
        self.assertEqual(len(found), 2)

    def test_repr(self):
        """It should return a string representation of an InventoryItem"""
        item = InventoryItem(name="TestItem", condition=Condition.NEW, quantity=1)
        item.id = 42
        self.assertEqual(repr(item), "<InventoryItem TestItem id=[42]>")

    def test_all_conditions_serialize(self):
        """It should correctly serialize each condition value"""
        for condition in Condition:
            item = InventoryItem(name="Test", condition=condition, quantity=1)
            item.create()
            data = item.serialize()
            self.assertEqual(data["condition"], condition.value)
            item.delete()
    def test_delete_an_inventory(self):
        """It should delete an Inventory item"""
        inventory = InventoryFactory()
        inventory.create()
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

    def test_deserialize_inventory_invalid_condition(self):
        """It should not deserialize when condition is not a valid enum value"""
        inventory = Inventory()
        payload = {
            "name": "keyboard",
            "product_id": "sku-1",
            "quantity_on_hand": 1,
            "restock_level": 1,
            "condition": "not_a_real_condition",
        }
        self.assertRaises(DataValidationError, inventory.deserialize, payload)

    def test_deserialize_inventory_bad_numeric_data(self):
        """It should not deserialize when numeric fields are wrong type (TypeError)"""
        inventory = Inventory()
        payload = {
            "name": "keyboard",
            "product_id": "sku-1",
            "quantity_on_hand": None,
            "restock_level": 2,
            "condition": "new",
        }
        self.assertRaises(DataValidationError, inventory.deserialize, payload)

    def test_repr(self):
        """It should provide a readable __repr__ for debugging"""
        inventory = InventoryFactory.build()
        text = repr(inventory)
        self.assertIn("Inventory", text)
        self.assertIn(str(inventory.product_id), text)

    def test_create_raises_when_commit_fails(self):
        """It should wrap DB failures on create as DataValidationError"""
        inventory = InventoryFactory.build()
        with patch.object(db.session, "commit", side_effect=RuntimeError("db down")):
            with self.assertRaises(DataValidationError):
                inventory.create()

    def test_update_persists_changes(self):
        """It should persist field changes with update()"""
        inventory = InventoryFactory()
        inventory.create()
        new_name = "renamed-item"
        inventory.name = new_name
        inventory.update()
        again = Inventory.find(inventory.id)
        self.assertIsNotNone(again)
        self.assertEqual(again.name, new_name)

    def test_update_raises_when_commit_fails(self):
        """It should wrap DB failures on update as DataValidationError"""
        inventory = InventoryFactory()
        inventory.create()
        inventory.name = "x"
        with patch.object(db.session, "commit", side_effect=RuntimeError("db down")):
            with self.assertRaises(DataValidationError):
                inventory.update()

    def test_delete_removes_record(self):
        """It should remove an inventory row with delete()"""
        inventory = InventoryFactory()
        inventory.create()
        iid = inventory.id
        inventory.delete()
        self.assertIsNone(Inventory.find(iid))

    def test_delete_raises_when_commit_fails(self):
        """It should wrap DB failures on delete as DataValidationError"""
        inventory = InventoryFactory()
        inventory.create()
        with patch.object(db.session, "commit", side_effect=RuntimeError("db down")):
            with self.assertRaises(DataValidationError):
                inventory.delete()

    def test_find_by_name(self):
        """It should return a query for inventories matching the given name"""
        target = "find-me-unique"
        InventoryFactory(name=target).create()
        InventoryFactory().create()
        result = Inventory.find_by_name(target)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().name, target)

    def test_find_low_stock(self):
        """It should return rows where quantity_on_hand <= restock_level"""
        InventoryFactory(quantity_on_hand=3, restock_level=10).create()
        InventoryFactory(quantity_on_hand=10, restock_level=10).create()
        InventoryFactory(quantity_on_hand=20, restock_level=5).create()
        found = Inventory.find_low_stock()
        self.assertEqual(len(found), 2)
        self.assertTrue(all(i.quantity_on_hand <= i.restock_level for i in found))

    def test_find_by_product_id(self):
        """It should return all inventories matching the given product_id"""
        pid = "prod-query-123"
        InventoryFactory(product_id=pid).create()
        InventoryFactory(product_id=pid).create()
        InventoryFactory(product_id="other").create()
        found = Inventory.find_by_product_id(pid)
        self.assertEqual(len(found), 2)
        self.assertTrue(all(i.product_id == pid for i in found))

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

    ######################################################################
    #  Q U E R Y   T E S T   C A S E S
    ######################################################################

    def test_find_by_condition(self):
        """It should find Inventory items by condition"""
        item1 = InventoryFactory(condition=ItemCondition.NEW)
        item2 = InventoryFactory(condition=ItemCondition.NEW)
        item3 = InventoryFactory(condition=ItemCondition.USED)

        item1.create()
        item2.create()
        item3.create()

        items = Inventory.find_by_condition(ItemCondition.NEW)
        self.assertEqual(len(items), 2)
        for item in items:
            self.assertEqual(item.condition, ItemCondition.NEW)
