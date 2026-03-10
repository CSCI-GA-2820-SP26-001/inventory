"""
Test Factory to make fake objects for testing
"""

import factory
from factory.fuzzy import FuzzyChoice, FuzzyInteger
from datetime import datetime

from service.models import Inventory, ItemCondition


class InventoryFactory(factory.Factory):
    """Factory for creating Inventory model instances for tests"""

    class Meta:  # pylint: disable=too-few-public-methods
        model = Inventory

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("word")
    product_id = factory.Faker("uuid4")
    quantity_on_hand = FuzzyInteger(0, 1000)
    restock_level = FuzzyInteger(0, 200)
    condition = FuzzyChoice(
        choices=[ItemCondition.NEW, ItemCondition.OPEN_BOX, ItemCondition.USED]
    )
    created_at = factory.LazyFunction(datetime.utcnow)
    last_updated = factory.LazyFunction(datetime.utcnow)
