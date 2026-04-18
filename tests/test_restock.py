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
TDD-style unit tests for PUT /inventory/<id>/restock.

Covers success, invalid quantity (400), not found (404), and JSON contract errors.
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase

from wsgi import app
from service.common import status
from service.models import db, Inventory
from tests.factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


class TestRestockAction(TestCase):
    """Inventory restock endpoint: PUT /inventory/<id>/restock."""

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
        db.session.query(Inventory).delete()
        db.session.commit()

    def tearDown(self):
        """Runs after each test"""
        db.session.remove()

    def test_restock_success_returns_updated_inventory(self):
        """Success: 200, JSON body reflects increased quantity_on_hand"""
        inventory = InventoryFactory(quantity_on_hand=10)
        inventory.create()
        add = 7
        resp = self.client.put(
            f"/inventory/{inventory.id}/restock",
            json={"amount": add},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], inventory.id)
        self.assertEqual(data["quantity_on_hand"], 10 + add)
        self.assertEqual(data["name"], inventory.name)
        self.assertEqual(data["product_id"], inventory.product_id)
        self.assertIn("restock_level", data)
        self.assertIn("condition", data)
        resp_get = self.client.get(f"/inventory/{inventory.id}")
        self.assertEqual(resp_get.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_get.get_json()["quantity_on_hand"], 10 + add)

    def test_restock_success_string_digits_accepted(self):
        """Quantity in JSON may be a string of digits; server coerces to int"""
        inventory = InventoryFactory(quantity_on_hand=3)
        inventory.create()
        resp = self.client.put(
            f"/inventory/{inventory.id}/restock",
            json={"amount": "12"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["quantity_on_hand"], 15)

    def test_restock_not_found_returns_404(self):
        """404 when no inventory row exists for the id"""
        resp = self.client.put(
            "/inventory/999999/restock",
            json={"amount": 5},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        body = resp.get_json()
        self.assertEqual(body.get("status"), status.HTTP_404_NOT_FOUND)

    def test_restock_invalid_quantity_missing_amount(self):
        """400 when amount is omitted"""
        inventory = InventoryFactory()
        inventory.create()
        resp = self.client.put(
            f"/inventory/{inventory.id}/restock",
            json={},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restock_invalid_quantity_null(self):
        """400 when amount is JSON null"""
        inventory = InventoryFactory()
        inventory.create()
        resp = self.client.put(
            f"/inventory/{inventory.id}/restock",
            json={"amount": None},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restock_invalid_quantity_zero(self):
        """400 when amount is zero"""
        inventory = InventoryFactory()
        inventory.create()
        resp = self.client.put(
            f"/inventory/{inventory.id}/restock",
            json={"amount": 0},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restock_invalid_quantity_negative(self):
        """400 when amount is negative"""
        inventory = InventoryFactory()
        inventory.create()
        resp = self.client.put(
            f"/inventory/{inventory.id}/restock",
            json={"amount": -3},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restock_invalid_quantity_non_numeric_string(self):
        """400 when amount is not parseable as an integer"""
        inventory = InventoryFactory()
        inventory.create()
        resp = self.client.put(
            f"/inventory/{inventory.id}/restock",
            json={"amount": "five"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restock_invalid_quantity_boolean(self):
        """400 when amount is JSON true/false (bool is not a restock quantity)"""
        inventory = InventoryFactory()
        inventory.create()
        for amount in (True, False):
            with self.subTest(amount=amount):
                resp = self.client.put(
                    f"/inventory/{inventory.id}/restock",
                    json={"amount": amount},
                    content_type="application/json",
                )
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restock_invalid_json_body(self):
        """400 when body is empty or not valid JSON"""
        inventory = InventoryFactory()
        inventory.create()
        resp = self.client.put(
            f"/inventory/{inventory.id}/restock",
            data="",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restock_wrong_content_type(self):
        """415 when Content-Type is not application/json"""
        inventory = InventoryFactory()
        inventory.create()
        resp = self.client.put(
            f"/inventory/{inventory.id}/restock",
            data='{"amount": 1}',
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
