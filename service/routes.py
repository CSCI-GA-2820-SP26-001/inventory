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
Inventory Service

REST API to create, read, update, and delete Inventory items.
"""

from flask import jsonify, request, url_for, abort, render_template
from flask import current_app as app  # Import Flask application
from service.models import Inventory, DataValidationError, ItemCondition
from service.common import status  # HTTP Status Codes


def _parse_low_stock_flag(raw: str | None) -> bool:
    """Return True when the low_stock query param requests the low-stock filter."""
    if raw is None:
        return False
    return raw.strip().lower() in ("true", "1", "yes")


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


@app.route("/health", methods=["GET"])
def health():
    """Health check for load balancers and orchestrators."""
    return jsonify({"status": "OK"}), status.HTTP_200_OK


######################################################################
# INVENTORY UI
######################################################################
@app.route("/ui", methods=["GET"])
def inventory_ui():
    """Serve a single-page inventory admin UI."""
    return render_template("inventory_ui.html"), status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

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


@app.route("/inventory/<int:inventory_id>", methods=["GET"])
def get_inventory(inventory_id):
    """Retrieve a single Inventory item."""
    inventory = Inventory.find(inventory_id)
    if not inventory:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Inventory with id '{inventory_id}' was not found.",
        )
    return jsonify(inventory.serialize()), status.HTTP_200_OK


@app.route("/inventory/<int:inventory_id>", methods=["PUT"])
def update_inventory(inventory_id):
    """Replace a single Inventory item (full update from JSON body)."""
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


######################################################################
# LIST INVENTORY ITEMS
######################################################################
@app.route("/inventory", methods=["GET"])
def list_inventory():
    """Returns all Inventory items, optionally filtered by ?product_id=<id>."""
    app.logger.info("Request for inventory list")

    items = []

    # Parse any arguments from the query string
    condition = request.args.get("condition")
    product_id = request.args.get("product_id")
    low_stock = request.args.get("low_stock")

    if condition:
        app.logger.info("Find by condition: %s", condition)
        try:
            condition_enum = ItemCondition(condition.lower())
        except ValueError:
            abort(status.HTTP_400_BAD_REQUEST, f"Invalid condition: {condition}")
        items = Inventory.find_by_condition(condition_enum)

    elif product_id:
        product_id = product_id.strip()
        app.logger.info("Find by product_id: %s", product_id)
        items = Inventory.find_by_product_id(product_id)

    elif low_stock:
        app.logger.info("Find by low_stock: %s", low_stock)
        low_stock_value = low_stock.lower() in ["true", "yes", "1"]
        if low_stock_value:
            items = Inventory.find_low_stock()
        else:
            items = Inventory.all()

    else:
        app.logger.info("Find all")
        items = Inventory.all()

    results = [item.serialize() for item in items]
    app.logger.info("Returning %d inventory items", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# RESTOCK AN Inventory ITEM
######################################################################
@app.route("/inventory/<int:inventory_id>/restock", methods=["PUT"])
def restock_inventory(inventory_id):
    """Increment quantity_on_hand by a positive integer amount."""
    if not request.is_json:
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Request Content-Type must be application/json",
        )
    data = request.get_json(silent=True)
    if data is None:
        raise DataValidationError("Request body must contain valid JSON")
    if "amount" not in data:
        raise DataValidationError("Request body must include 'amount'")
    raw_amount = data["amount"]
    if isinstance(raw_amount, bool):
        raise DataValidationError("Invalid amount: must be a positive integer")
    try:
        amount = int(raw_amount)
    except (TypeError, ValueError) as exc:
        raise DataValidationError("Invalid amount: must be a positive integer") from exc
    if amount < 1:
        raise DataValidationError("Invalid amount: must be a positive integer")

    inventory = Inventory.find(inventory_id)
    if not inventory:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Inventory with id '{inventory_id}' was not found.",
        )

    app.logger.info("Restock inventory id [%s] by amount [%s]", inventory_id, amount)
    inventory.quantity_on_hand += amount
    inventory.update()
    return jsonify(inventory.serialize()), status.HTTP_200_OK


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
