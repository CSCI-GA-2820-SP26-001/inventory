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

"""Inventory service routes and Flask-RESTX resources."""

from flask import jsonify, request, abort
from flask import current_app as app
from flask_restx import Api, Namespace, Resource
from service.models import Inventory, DataValidationError, ItemCondition
from service.common import status

api = Api(
    app,
    version="1.0",
    title="Inventory API",
    description="Inventory REST API",
    prefix="/api",
    doc="/api/docs",
)
inventory_ns = Namespace("inventory", description="Inventory operations", path="/inventory")
api.add_namespace(inventory_ns)


def _parse_low_stock_flag(raw: str | None) -> bool:
    """Return True when the low_stock query param requests the low-stock filter."""
    if raw is None:
        return False
    return raw.strip().lower() in ("true", "1", "yes")


def _service_info():
    """Service metadata payload used by index endpoints."""
    return (
        jsonify(
            name=app.config["SERVICE_NAME"],
            version=app.config["VERSION"],
            url=request.base_url.rstrip("/"),
        ),
        status.HTTP_200_OK,
    )


def _list_inventory_impl():
    """Returns all Inventory items, optionally filtered by query params."""
    app.logger.info("Request for inventory list")
    condition = request.args.get("condition")
    product_id = request.args.get("product_id")
    low_stock = request.args.get("low_stock")
@app.route("/favicon.ico")
def favicon():
    """Browsers request this automatically; avoid noisy 404s in logs."""
    return "", status.HTTP_204_NO_CONTENT


@app.route("/health", methods=["GET"])
def health():
    """Health check for load balancers and orchestrators."""
    return jsonify({"status": "OK"}), status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

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
    elif _parse_low_stock_flag(low_stock):
        app.logger.info("Find by low_stock: %s", low_stock)
        items = Inventory.find_low_stock()
    else:
        app.logger.info("Find all")
        items = Inventory.all()

    results = [item.serialize() for item in items]
    app.logger.info("Returning %d inventory items", len(results))
    return jsonify(results), status.HTTP_200_OK


def _create_inventory_impl():
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
    location = f"{request.url_root.rstrip('/')}/api/inventory/{inventory.id}"
    return (
        jsonify(inventory.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location},
    )


def _get_inventory_impl(inventory_id: int):
    """Retrieve a single Inventory item."""
    inventory = Inventory.find(inventory_id)
    if not inventory:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Inventory with id '{inventory_id}' was not found.",
        )
    return jsonify(inventory.serialize()), status.HTTP_200_OK


def _update_inventory_impl(inventory_id: int):
    """Replace a single Inventory item from JSON body."""
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


def _delete_inventory_impl(inventory_id: int):
    """Delete an inventory item."""
    app.logger.info("Request to delete an inventory item with id [%s]", inventory_id)
    inventory = Inventory.find(inventory_id)
    if inventory:
        app.logger.info("Item with ID: %d found.", inventory_id)
        inventory.delete()
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
        app.logger.info(
            "Item with ID: %d not found; returning 204 for idempotent DELETE.",
            inventory_id,
        )
    return "", status.HTTP_204_NO_CONTENT


def _restock_inventory_impl(inventory_id: int):
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


@inventory_ns.route("")
class InventoryCollectionResource(Resource):
    """Inventory collection resource."""

    def get(self):
        return _list_inventory_impl()

    def post(self):
        return _create_inventory_impl()


@inventory_ns.route("/<int:inventory_id>")
class InventoryItemResource(Resource):
    """Inventory item resource."""

    def get(self, inventory_id: int):
        return _get_inventory_impl(inventory_id)

    def put(self, inventory_id: int):
        return _update_inventory_impl(inventory_id)

    def delete(self, inventory_id: int):
        return _delete_inventory_impl(inventory_id)


@inventory_ns.route("/<int:inventory_id>/restock")
class InventoryRestockResource(Resource):
    """Inventory restock action resource."""

    def put(self, inventory_id: int):
        return _restock_inventory_impl(inventory_id)


@app.route("/")
def index():
    """Root URL response - returns service info as JSON."""
    return _service_info()


@app.route("/api")
def api_index():
    """API root URL response."""
    return _service_info()


@app.route("/favicon.ico")
def favicon():
    """Browsers request this automatically; avoid noisy 404s in logs."""
    return "", status.HTTP_204_NO_CONTENT


@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health():
    """Health check for load balancers and orchestrators."""
    return jsonify({"status": "OK"}), status.HTTP_200_OK


# Legacy compatibility routes
@app.route("/inventory", methods=["GET"])
def list_inventory():
    """Compatibility wrapper for legacy route."""
    return _list_inventory_impl()


@app.route("/inventory", methods=["POST"])
def create_inventory():
    """Compatibility wrapper for legacy route."""
    return _create_inventory_impl()


@app.route("/inventory/<int:inventory_id>", methods=["GET"])
def get_inventory(inventory_id):
    """Compatibility wrapper for legacy route."""
    return _get_inventory_impl(inventory_id)


@app.route("/inventory/<int:inventory_id>", methods=["PUT"])
def update_inventory(inventory_id):
    """Compatibility wrapper for legacy route."""
    return _update_inventory_impl(inventory_id)


@app.route("/inventory/<int:inventory_id>", methods=["DELETE"])
def delete_inventory_item(inventory_id):
    """Compatibility wrapper for legacy route."""
    return _delete_inventory_impl(inventory_id)


@app.route("/inventory/<int:inventory_id>/restock", methods=["PUT"])
def restock_inventory(inventory_id):
    """Compatibility wrapper for legacy route."""
    return _restock_inventory_impl(inventory_id)
