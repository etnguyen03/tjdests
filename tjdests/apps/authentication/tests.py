from django.contrib.auth.hashers import check_password
from django.urls import reverse

from ...test import TJDestsTestCase
from .models import User


class AuthenticationTest(TJDestsTestCase):
    def test_index_page(self):
        """Tests the index page."""
        response = self.client.get(reverse("authentication:index"))
        self.assertEqual(200, response.status_code)

        # Login and ensure that works
        self.login()
        response = self.client.get(reverse("authentication:index"))
        self.assertEqual(200, response.status_code)

        self.login(make_senior=True, make_student=True, accept_tos=True)
        response = self.client.get(reverse("authentication:index"))
        self.assertEqual(200, response.status_code)

    def test_tos_view(self):
        """Tests the accept TOS and set permanent password view."""

        # The user needs to be logged in
        response = self.client.get(reverse("authentication:tos"))
        self.assertEqual(302, response.status_code)

        # A non-student should be logged out
        self.login(make_student=False)
        response = self.client.get(reverse("authentication:tos"))
        self.assertEqual(302, response.status_code)
        self.assertNotIn("_auth_user_id", self.client.session)

        # Make us a student and try again
        user = self.login(make_student=True)
        response = self.client.get(reverse("authentication:tos"))
        self.assertEqual(200, response.status_code)

        # POST but leave everything blank (because why not)
        response = self.client.post(reverse("authentication:tos"))
        self.assertEqual(200, response.status_code)

        # POST but don't accept TOS
        response = self.client.post(
            reverse("authentication:tos"),
            data={
                "accept_tos": False,
                "password": "dankmemes",
                "password_confirm": "dankmemes",
                "understand_no_reset": True,
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertIn(
            "You must accept the license terms to continue.",
            response.content.decode("UTF-8"),
        )

        # POST but don't understand that there's no password reset
        response = self.client.post(
            reverse("authentication:tos"),
            data={
                "accept_tos": True,
                "password": "dankmemes",
                "password_confirm": "dankmemes",
                "understand_no_reset": False,
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertIn(
            "You must acknowledge that there is no password reset to continue.",
            response.content.decode("UTF-8"),
        )

        # POST - password too weak
        response = self.client.post(
            reverse("authentication:tos"),
            data={
                "accept_tos": True,
                "password": "d",
                "password_confirm": "d",
                "understand_no_reset": True,
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertIn("This password is too short", response.content.decode("UTF-8"))

        response = self.client.post(
            reverse("authentication:tos"),
            data={
                "accept_tos": True,
                "password": "dssssssssssss",
                "password_confirm": "fsdfsdfs",
                "understand_no_reset": True,
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertIn(
            "The two passwords do not match", response.content.decode("UTF-8")
        )

        # POST, this should work
        response = self.client.post(
            reverse("authentication:tos"),
            data={
                "accept_tos": True,
                "password": "dankmemes",
                "password_confirm": "dankmemes",
                "understand_no_reset": True,
            },
        )
        self.assertEqual(302, response.status_code)

        # Assert accepted TOS and password hashes
        self.assertEqual(
            1, User.objects.filter(accepted_terms=True, id=user.id).count()
        )
        self.assertTrue(
            check_password("dankmemes", User.objects.get(id=user.id).password)
        )

        # Loading the page now should 302
        response = self.client.get(reverse("authentication:tos"))
        self.assertEqual(302, response.status_code)
