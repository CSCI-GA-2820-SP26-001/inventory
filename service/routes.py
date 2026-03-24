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
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Inventory, DataValidationError
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response - returns service info as JSON."""
    return jsonify(
        name=app.config["SERVICE_NAME"],
        version=app.config["VERSION"],
        url=request.base_url.rstrip("/"),
    ), status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if request.mimetype != content_type:
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )


@app.route("/inventory", methods=["POST"])
def create_inventory():
    """Create an Inventory item"""
    app.logger.info("Request to Create an Inventory item...")
    check_content_type("application/json")

    data = request.get_json()
    app.logger.info("Processing: %s", data)

    inventory = Inventory()
    try:
        inventory.deserialize(data)
    except DataValidationError as error:
        abort(status.HTTP_400_BAD_REQUEST, str(error))

    inventory.create()
    app.logger.info("Inventory item with new id [%s] saved!", inventory.id)

    location_url = url_for("get_inventory", inventory_id=inventory.id, _external=True)
    return (
        jsonify(inventory.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


@app.route("/inventory/<int:inventory_id>", methods=["GET"])
def get_inventory(inventory_id):
    """Retrieve a single Inventory item"""
    inventory = Inventory.find(inventory_id)
    if not inventory:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Inventory with id '{inventory_id}' was not found.",
        )
    return jsonify(inventory.serialize()), status.HTTP_200_OK
