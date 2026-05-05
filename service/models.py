"""Data models for the Inventory service."""

import logging
from enum import Enum

from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for data validation errors when deserializing."""


class ItemCondition(Enum):
    """Enumeration of valid inventory item conditions."""

    NEW = "new"
    OPEN_BOX = "open_box"
    USED = "used"


class Inventory(db.Model):
    """Represents an inventory item in the database."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    product_id = db.Column(db.String(64), nullable=False)
    quantity_on_hand = db.Column(db.Integer, nullable=False, default=0)
    restock_level = db.Column(db.Integer, nullable=False, default=0)
    condition = db.Column(
        db.Enum(ItemCondition), nullable=False, server_default=ItemCondition.NEW.name
    )
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    last_updated = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )

    def __repr__(self):
        return f"<Inventory {self.name} product_id=[{self.product_id}] id=[{self.id}]>"

    def create(self):
        """Persist a new Inventory record to the database."""
        self.id = None
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as error:  # pylint: disable=broad-except
            db.session.rollback()
            raise DataValidationError(error) from error

    def update(self):
        """Persist changes to this Inventory record."""
        try:
            db.session.commit()
        except Exception as error:  # pylint: disable=broad-except
            db.session.rollback()
            raise DataValidationError(error) from error

    def delete(self):
        """Remove this Inventory record from the database."""
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as error:  # pylint: disable=broad-except
            db.session.rollback()
            raise DataValidationError(error) from error

    def serialize(self):
        """Serialize this record to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "product_id": self.product_id,
            "quantity_on_hand": self.quantity_on_hand,
            "restock_level": self.restock_level,
            "condition": self.condition.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

    def deserialize(self, data):
        """Deserialize an Inventory item from a dictionary."""
        try:
            self.name = data["name"]
            self.product_id = data["product_id"]
            self.quantity_on_hand = int(data["quantity_on_hand"])
            self.restock_level = int(data["restock_level"])
            self.condition = ItemCondition(data["condition"])
        except ValueError as error:
            raise DataValidationError("Invalid value: " + str(error)) from error
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError("Invalid Inventory: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError("Invalid Inventory: bad or no data " + str(error)) from error
        return self

    @classmethod
    def all(cls):
        """Return all Inventory rows in the database."""
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Find an Inventory row by ID."""
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Return all Inventory rows with the given name."""
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_low_stock(cls):
        """Return rows where quantity_on_hand <= restock_level."""
        return cls.query.filter(cls.quantity_on_hand <= cls.restock_level).all()

    @classmethod
    def find_by_product_id(cls, product_id: str):
        """Return all Inventory rows with the given product_id."""
        return cls.query.filter(cls.product_id == product_id).all()

    @classmethod
    def find_by_condition(cls, condition: ItemCondition):
        """Return all Inventory rows with the given condition."""
        return cls.query.filter(cls.condition == condition).all()
