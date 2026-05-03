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

"""Tests for service.common.error_handlers"""

import logging
import os
from unittest import TestCase

from wsgi import app
from service.common import error_handlers, status

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  E R R O R   H A N D L E R S
######################################################################
class TestErrorHandlers(TestCase):
    """Exercise Flask error handlers registered in error_handlers"""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        cls._app_ctx = app.app_context()
        cls._app_ctx.push()

    @classmethod
    def tearDownClass(cls):
        cls._app_ctx.pop()

    def test_method_not_supported_returns_json(self):
        """405 handler should log a warning and return JSON with status 405"""
        err = Exception("Method Not Allowed")
        with app.test_request_context():
            response, code = error_handlers.method_not_supported(err)
        self.assertEqual(code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = response.get_json()
        self.assertEqual(data["error"], "Method not Allowed")
        self.assertEqual(data["status"], status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertIn("Method Not Allowed", data["message"])

    def test_internal_server_error_returns_json(self):
        """500 handler should log an error and return JSON with status 500"""
        err = Exception("Something broke")
        with app.test_request_context():
            response, code = error_handlers.internal_server_error(err)
        self.assertEqual(code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = response.get_json()
        self.assertEqual(data["error"], "Internal Server Error")
        self.assertEqual(data["status"], status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Something broke", data["message"])
