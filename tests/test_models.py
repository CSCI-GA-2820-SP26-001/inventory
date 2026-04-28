"""
Test cases for InventoryItem Model
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import InventoryItem, Condition, DataValidationError, db
from .factories import InventoryItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  I N V E N T O R Y   I T E M   M O D E L   T E S T   C A S E S
######################################################################
class TestInventoryItemModel(TestCase):
    """Test Cases for InventoryItem Model"""

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
