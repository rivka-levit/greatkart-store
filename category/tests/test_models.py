import pytest

from django.db.utils import IntegrityError

from category.models import Category

pytestmark = pytest.mark.django_db


def test_create_category_success() -> None:
    """Test creating category with right fields successfully."""

    payload = {
        'category_name': 'Test Category',
        'slug': 'test-category',
        'description': 'Some test category'
    }

    category = Category.objects.create(**payload)

    assert category.category_name == payload['category_name']
    assert category.slug == payload['slug']
    assert category.description == payload['description']
    assert str(category) == payload['category_name']


def test_create_category_not_unique_name_fails(category) -> None:
    """Test creating category with not unique name fails."""

    category(category_name='Shoes', slug='shoes')

    with pytest.raises(IntegrityError):
        Category.objects.create(category_name='Shoes', slug='shoes')


