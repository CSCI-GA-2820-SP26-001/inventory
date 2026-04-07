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
    return (
        jsonify(
            name=app.config["SERVICE_NAME"],
            version=app.config["VERSION"],
            url=request.base_url.rstrip("/"),
        ),
        status.HTTP_200_OK,
    )


@app.route("/favicon.ico")
def favicon():
    """Browsers request this automatically; avoid noisy 404s in logs."""
    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...

######################################################################
# DELETE AN Inventory Item
######################################################################


@app.route("/inventory/<int:product_id>", methods=["DELETE"])
def delete_inventory_item(product_id):
    """
    Delete an inventory item
    This endpoint deletes an inventory item based on product id
    """
    app.logger.info("Request to delete an inventory item with id [%s]", product_id)

    inventory = Inventory.find(product_id)
    if inventory:
        app.logger.info("Item with ID: %d found.", product_id)
        inventory.delete()
    else:
        app.logger.info(
            "Item with ID: %d not found; returning 204 for idempotent DELETE.",
            product_id,
        )
    return "", status.HTTP_204_NO_CONTENT


@app.route("/inventory/<int:inventory_id>", methods=["GET", "PUT"])
def get_inventory(inventory_id):
    """Retrieve (GET) or replace (PUT) a single Inventory item."""
    if request.method == "PUT":
        if not request.is_json:
            abort(
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                "Request Content-Type must be application/json",
            )
        data = request.get_json(silent=True)
        if data is None:
            raise DataValidationError("Request body must contain valid JSON")

        inventory = Inventory.find(inventory_id)
        if not inventory:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Inventory with id '{inventory_id}' was not found.",
            )
        inventory.deserialize(data)
        inventory.update()
        return jsonify(inventory.serialize()), status.HTTP_200_OK

    inventory = Inventory.find(inventory_id)
    if not inventory:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Inventory with id '{inventory_id}' was not found.",
        )
    return jsonify(inventory.serialize()), status.HTTP_200_OK


######################################################################
# LIST ALL INVENTORY ITEMS
######################################################################
@app.route("/inventory", methods=["GET"])
def list_inventory():
    """Returns all Inventory items"""
    app.logger.info("Request for inventory list")

    inventory = Inventory.all()

    results = [item.serialize() for item in inventory]

    app.logger.info("Returning %d inventory items", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# CREATE AN Inventory ITEM
######################################################################
@app.route("/inventory", methods=["POST"])
def create_inventory():
    """Create an Inventory item from JSON payload."""
    if not request.is_json:
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Request Content-Type must be application/json",
        )
    data = request.get_json(silent=True)
    if data is None:
        raise DataValidationError("Request body must contain valid JSON")

    inventory = Inventory()
    inventory.deserialize(data)
    inventory.create()

    location = url_for("get_inventory", inventory_id=inventory.id, _external=True)
    return (
        jsonify(inventory.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location},
    )
