"""
Models for YourResourceModel

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy
from enum import Enum

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class ItemCondition(Enum):
    """Enumeration of valid inventory item conditions"""

    NEW = "new"
    OPEN_BOX = "open_box"
    USED = "used"


class Inventory(db.Model):
    """
    Class that represents a YourResourceModel
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))

    product_id = db.Column(db.String(64), nullable=False)

    quantity_on_hand = db.Column(db.Integer, nullable=False, default=0)

    restock_level = db.Column(db.Integer, nullable=False, default=0)

    condition = db.Column(
        db.Enum(ItemCondition), nullable=False, server_default=ItemCondition.NEW.name
    )

    # database auditing fields

    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    last_updated = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )

    def __repr__(self):
        return f"<YourResourceModel {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a YourResourceModel to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a YourResourceModel to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes an inventory item from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a YourResourceModel into a dictionary"""
        condition_val = (
            self.condition.value if self.condition is not None else None
        )
        return {
            "id": self.id,
            "name": self.name,
            "product_id": self.product_id,
            "quantity_on_hand": self.quantity_on_hand,
            "restock_level": self.restock_level,
            "condition": condition_val,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": (
                self.last_updated.isoformat() if self.last_updated else None
            ),
        }

    def deserialize(self, data):
        """
        Deserializes a YourResourceModel from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.product_id = data["product_id"]
            self.quantity_on_hand = int(data["quantity_on_hand"])
            self.restock_level = int(data["restock_level"])
            self.condition = ItemCondition(data["condition"])
        except KeyError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: missing " + error.args[0]
            ) from error
        except ValueError as error:
            raise DataValidationError("Invalid value: " + str(error)) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the YourResourceModels in the database"""
        logger.info("Processing all YourResourceModels")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a YourResourceModel by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all YourResourceModels with the given name

        Args:
            name (string): the name of the YourResourceModels you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
