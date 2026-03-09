from flask import Flask, request, jsonify, abort
from models import Inventory, ItemCondition, DataValidationError, db

app = Flask(__name__)


@app.route("/inventory", methods=["POST"])
def create_inventory():
    """Creates a new Inventory record"""
    data = request.get_json()
    if not data:
        abort(400, description="Request body must be JSON")

    inventory = Inventory()
    try:
        inventory.deserialize(data)
    except DataValidationError as e:
        abort(400, description=str(e))

    inventory.create()
    return jsonify(inventory.serialize()), 201


def serialize(self):
    """Serializes an Inventory into a dictionary"""
    return {
        "id": self.id,
        "name": self.name,
        "product_id": self.product_id,
        "quantity_on_hand": self.quantity_on_hand,
        "restock_level": self.restock_level,
        "condition": self.condition.value,
        "created_at": self.created_at.isoformat(),
        "last_updated": self.last_updated.isoformat(),
    }


def deserialize(self, data):
    """Deserializes an Inventory from a dictionary"""
    try:
        self.name = data["name"]
        self.product_id = data["product_id"]
        self.quantity_on_hand = int(data["quantity_on_hand"])
        self.restock_level = int(data["restock_level"])

        condition_value = data["condition"]
        self.condition = ItemCondition(condition_value)  # raises ValueError if invalid

    except ValueError as error:
        raise DataValidationError(f"Invalid value: {error}") from error
    except KeyError as error:
        raise DataValidationError("Missing field: " + error.args[0]) from error
    except TypeError as error:
        raise DataValidationError(
            "Bad or no data in request body: " + str(error)
        ) from error
    return self
