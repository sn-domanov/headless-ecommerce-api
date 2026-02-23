from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.products.api.v1.serializers import CategorySerializer
from apps.products.models import Category

User = get_user_model()


class CategorySerializerTest(TestCase):
    def test_category_serializer_parent_name(self):
        parent = Category.objects.create(name="Parent")
        child = Category.objects.create(name="Child", parent=parent)
        serialized = CategorySerializer(child).data

        self.assertEqual(serialized["parent_name"], "Parent")
