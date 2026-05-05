"""
Behave environment setup for BDD tests
"""

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from wsgi import app
from service.models import Inventory, db
from service.models import db, Inventory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8080")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")


def before_all(context):
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    context.app = app
    context.app_context = app.app_context()
    context.app_context.push()
    db.create_all()
    context.client = app.test_client()
    context.base_url = BASE_URL
    context.browser = None

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(CHROMEDRIVER_PATH)
    try:
        context.browser = webdriver.Chrome(service=service, options=options)
    except Exception:  # pragma: no cover - browser availability is environment-dependent
        context.browser = None


def after_all(context):
    if context.browser is not None:
        context.browser.quit()
    db.session.close()
    context.app_context.pop()


def before_scenario(context, scenario):
    db.session.query(Inventory).delete()
    db.session.commit()


def after_scenario(context, scenario):
    db.session.remove()
