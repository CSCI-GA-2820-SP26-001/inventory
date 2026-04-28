"""
Models for Inventory

All of the models are stored in this module
"""

import logging
import enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for data validation errors when deserializing"""


class Condition(enum.Enum):
    """Condition states for an inventory item"""

    NEW = "new"
    USED = "used"
    OPEN_BOX = "open_box"


class InventoryItem(db.Model):
    """
    Class that represents an InventoryItem
    """

    __tablename__ = "inventory_item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    condition = db.Column(
        db.Enum(Condition), nullable=False, default=Condition.NEW
    )
    quantity = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<InventoryItem {self.name} id=[{self.id}]>"

    def create(self):
        """Creates an InventoryItem in the database"""
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
        """Updates an InventoryItem in the database"""
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes an InventoryItem from the database"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes an InventoryItem into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "condition": self.condition.value,
            "quantity": self.quantity,
        }

    def deserialize(self, data):
        """
        Deserializes an InventoryItem from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            condition_value = data["condition"]
            self.condition = Condition(condition_value)
            self.quantity = int(data["quantity"])
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid InventoryItem: missing " + error.args[0]
            ) from error
        except (TypeError, ValueError) as error:
            raise DataValidationError(
                "Invalid InventoryItem: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all InventoryItems in the database"""
        logger.info("Processing all InventoryItems")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds an InventoryItem by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all InventoryItems with the given name

        Args:
            name (string): the name of the InventoryItems you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_condition(cls, condition):
        """Returns all InventoryItems with the given condition

        Args:
            condition (Condition): the condition enum value to match
        """
        logger.info("Processing condition query for %s ...", condition)
        return cls.query.filter(cls.condition == condition)
