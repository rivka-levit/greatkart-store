import pytest

from category.models import Category

from collections.abc import Callable


@pytest.fixture
def shoes() -> Category:
    return Category(
        category_name='Shoes',
        slug='shoes'
    )


@pytest.fixture
def category(**kwargs) -> Callable:
    def _create_category(**kwargs) -> Category:
        return Category.objects.create(**kwargs)
    return _create_category
