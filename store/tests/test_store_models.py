"""Tests for models in store app."""

import pytest

from store.models import Product

pytestmark = pytest.mark.django_db


def test_create_product_success(category) -> None:
    """Test creating product successfully."""

    cat = category(category_name='Shoes')
    payload = {
        'product_name': 'Some Shoes',
        'slug': 'some-shoes',
        'price': 359,
        'stock': 38,
        'category': cat,
    }

    p = Product.objects.create(**payload)

    assert str(p) == payload['product_name']
    assert p.slug == payload['slug']
    assert p.price == payload['price']
    assert p.stock == payload['stock']
    assert p.category == payload['category']
