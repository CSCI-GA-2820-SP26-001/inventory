"""
Behave environment setup for BDD tests
"""

import os
from wsgi import app
from service.models import db, InventoryItem

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


def before_all(context):
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    context.app = app
    context.app_context = app.app_context()
    context.app_context.push()
    db.create_all()
    context.client = app.test_client()


def after_all(context):
    db.session.close()
    context.app_context.pop()


def before_scenario(context, scenario):
    db.session.query(InventoryItem).delete()
    db.session.commit()


def after_scenario(context, scenario):
    db.session.remove()
