from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.forms import ValidationError
from django.test import TestCase

User = get_user_model()


class UserModelTestCase(TestCase):
    def test_create_user_with_email(self):
        """
        Test creating a user with email.
        """
        email = "johndoe@example.com"
        password = "Securep@ssword-123"

        user = User.objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)

        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """
        Test creating a superuser with email.
        """
        email = "admin@example.com"
        password = "AdminPass123!"

        user = User.objects.create_superuser(
            email=email,
            password=password,
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
