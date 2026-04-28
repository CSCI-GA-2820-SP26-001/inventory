"""
Test Factory to make fake objects for testing
"""

import factory
from factory.fuzzy import FuzzyChoice
from service.models import InventoryItem, Condition


class InventoryItemFactory(factory.Factory):
    """Creates fake inventory items for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = InventoryItem

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("word")
    condition = FuzzyChoice(list(Condition))
    quantity = factory.Faker("pyint", min_value=0, max_value=500)
