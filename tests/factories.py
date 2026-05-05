"""Test factories for inventory model instances."""

from datetime import datetime

import factory
from factory.fuzzy import FuzzyChoice, FuzzyInteger

from service.models import Inventory, ItemCondition


class InventoryFactory(factory.Factory):
    """Factory for creating Inventory model instances for tests."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Map factory to data model."""

        model = Inventory

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("word")
    product_id = factory.Sequence(lambda n: f"SKU-{n+1:04d}")
    quantity_on_hand = FuzzyInteger(0, 1000)
    restock_level = FuzzyInteger(0, 200)
    condition = FuzzyChoice(
        choices=[ItemCondition.NEW, ItemCondition.OPEN_BOX, ItemCondition.USED]
    )
    created_at = factory.LazyFunction(datetime.utcnow)
    last_updated = factory.LazyFunction(datetime.utcnow)
