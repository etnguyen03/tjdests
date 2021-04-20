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
    ) -> User:
        """
        Log in as the specified user.

        Args:
            username: The username to log in as.
            accept_tos: Whether to accept the terms or not.
            make_student: Whether to make this user a student.
            make_senior: Whether to make this user a senior.
            make_superuser: Whether to make this user a superuser.
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
                "accepted_terms": accept_tos,
            },
        )[0]
        self.client.force_login(user)
        return user
