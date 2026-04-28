"""
Inventory Service

This service implements a REST API for managing inventory items.
"""

from flask import jsonify, render_template
from flask import current_app as app
from service.models import InventoryItem
from service.common import status


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Serve the inventory management UI"""
    return render_template("index.html")


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


@app.route("/api/inventory", methods=["GET"])
def list_inventory():
    """Returns all inventory items"""
    app.logger.info("Request to list all inventory items")
    items = InventoryItem.all()
    results = [item.serialize() for item in items]
    app.logger.info("Returning %d inventory items", len(results))
    return jsonify(results), status.HTTP_200_OK
