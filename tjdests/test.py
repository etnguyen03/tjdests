from django.http import HttpRequest
from django.test import TestCase

from tjdests.apps.authentication.models import User


class TJDestsTestCase(TestCase):
    def login(  # pylint: disable=too-many-arguments
        self,
        username: str = "awilliam",
        accept_tos: bool = False,
        make_student: bool = False,
        make_senior: bool = False,
        make_superuser: bool = False,
        ban_user: bool = False,
        publish_data: bool = False,
    ) -> User:
        """
        Log in as the specified user.

        Args:
            username: The username to log in as.
            accept_tos: Whether to accept the terms or not.
            make_student: Whether to make this user a student.
            make_senior: Whether to make this user a senior.
            make_superuser: Whether to make this user a superuser.
            ban_user: Whether to ban the user.
            publish_data: Whether to publish this user's data.
        Return:
            The user.
        """
        user = User.objects.update_or_create(
            username=username,
            defaults={
                "is_student": make_student,
                "is_staff": make_superuser,
                "is_superuser": make_superuser,
                "is_senior": make_senior,
                "is_banned": ban_user,
                "accepted_terms": accept_tos,
                "publish_data": publish_data,
            },
        )[0]
        user.set_password("hello123")
        user.save()
        self.client.login(username=username, password="hello123", request=HttpRequest())
        return user
