from unittest.mock import mock_open, patch

from django.core.management import CommandError, call_command
from django.urls import reverse

from ...test import TJDestsTestCase
from .models import College, Decision


class DestinationsTest(TJDestsTestCase):
    """Tests the destinations app."""

    def test_destinations_list(self):
        """Tests the destinations list page."""
        # Test as an unauthenticated user.
        response = self.client.get(reverse("destinations:students"))
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            reverse("authentication:login")
            + f"?next={reverse('destinations:students')}",
            response.url,
        )

        self.login(make_student=True, accept_tos=True)

        # Load the page
        response = self.client.get(reverse("destinations:students"))
        self.assertEqual(200, response.status_code)

        # Make us a senior
        user = self.login(make_student=True, make_senior=True, accept_tos=True)
        user.publish_data = True
        user.save()

        # Add a destination
        college = College.objects.get_or_create(name="test college")[0]
        Decision.objects.get_or_create(
            college=college, user=user, decision_type="ED", admission_status="ADMIT"
        )

        response = self.client.get(reverse("destinations:students"))
        self.assertEqual(200, response.status_code)
        self.assertIn(user, response.context["object_list"])
        self.assertIn(college.name, response.content.decode("UTF-8"))
        self.assertIn("ED", response.content.decode("UTF-8"))
        self.assertIn("fa-check", response.content.decode("UTF-8"))

        # Add another user, but add us a name first
        user.first_name = "Angela"
        user.last_name = "William"
        user.save()

        user2 = self.login(
            make_student=True,
            username="2021awilliam",
            make_senior=True,
            accept_tos=True,
        )
        user2.first_name = "Adam"
        user2.last_name = "William"
        user2.nickname = "John"
        user2.save()

        college2 = College.objects.get_or_create(name="university of test")[0]
        Decision.objects.get_or_create(
            college=college2, user=user2, decision_type="ED", admission_status="DENY"
        )

        response = self.client.get(reverse("destinations:students"))
        self.assertEqual(200, response.status_code)
        self.assertIn(user, response.context["object_list"])
        self.assertNotIn(
            user2, response.context["object_list"]
        )  # haven't published data

        # Check superuser "all" get parameter
        # We are not a superuser, so this should 403.
        response = self.client.get(reverse("destinations:students"), data={"all": True})
        self.assertEqual(403, response.status_code)

        # Make us a superuser.
        user2.is_superuser = True
        user2.is_staff = True
        user2.save()

        response = self.client.get(reverse("destinations:students"))
        self.assertEqual(200, response.status_code)
        self.assertIn(user, response.context["object_list"])
        self.assertNotIn(user2, response.context["object_list"])

        # with the "all" parameter, this should return with user2 and user
        response = self.client.get(reverse("destinations:students"), data={"all": True})
        self.assertEqual(200, response.status_code)
        self.assertIn(user, response.context["object_list"])
        self.assertIn(user2, response.context["object_list"])
        self.assertIn(user, response.context["object_list"])

        user2.is_superuser = False
        user2.is_staff = False
        user2.save()

        user2.publish_data = True
        user2.save()

        response = self.client.get(reverse("destinations:students"))
        self.assertEqual(200, response.status_code)
        self.assertIn(user, response.context["object_list"])
        self.assertIn(user2, response.context["object_list"])

        # Now, test searching
        response = self.client.get(
            reverse("destinations:students"), data={"q": "Angela"}
        )
        self.assertEqual(200, response.status_code)
        self.assertIn(user, response.context["object_list"])
        self.assertNotIn(user2, response.context["object_list"])

        # Adam "John" William should show up when searching "Adam", his first name...
        response = self.client.get(reverse("destinations:students"), data={"q": "Adam"})
        self.assertEqual(200, response.status_code)
        self.assertNotIn(user, response.context["object_list"])
        self.assertIn(user2, response.context["object_list"])

        # ...and he should show up when searching "John", his middle name
        response = self.client.get(reverse("destinations:students"), data={"q": "John"})
        self.assertEqual(200, response.status_code)
        self.assertNotIn(user, response.context["object_list"])
        self.assertIn(user2, response.context["object_list"])

        response = self.client.get(
            reverse("destinations:students"), data={"q": "William"}
        )
        self.assertEqual(200, response.status_code)
        self.assertIn(user, response.context["object_list"])
        self.assertIn(user2, response.context["object_list"])

        # Test filtering by college
        response = self.client.get(
            reverse("destinations:students"), data={"college": college.id}
        )
        self.assertEqual(200, response.status_code)
        self.assertIn(user, response.context["object_list"])
        self.assertNotIn(user2, response.context["object_list"])

        # Non alphanumeric should 404
        response = self.client.get(
            reverse("destinations:students"), data={"college": str(college.id) + "f"}
        )
        self.assertEqual(404, response.status_code)

        # Non existent should 404
        # sanity check
        assert College.objects.filter(id=college.id + 5).count() == 0

        response = self.client.get(
            reverse("destinations:students"), data={"college": college.id + 5}
        )
        self.assertEqual(404, response.status_code)

        response = self.client.get(
            reverse("destinations:students"), data={"college": college2.id}
        )
        self.assertEqual(200, response.status_code)
        self.assertNotIn(user, response.context["object_list"])
        self.assertIn(user2, response.context["object_list"])

        # nonexist should 404
        response = self.client.get(
            reverse("destinations:students"), data={"college": "9999"}
        )
        self.assertEqual(404, response.status_code)

        # Test filtering with both at the same time
        response = self.client.get(
            reverse("destinations:students"),
            data={"college": college.id, "q": "Angela"},
        )
        self.assertEqual(200, response.status_code)
        self.assertIn(user, response.context["object_list"])
        self.assertNotIn(user2, response.context["object_list"])

        response = self.client.get(
            reverse("destinations:students"), data={"college": college.id, "q": "Adam"}
        )
        self.assertEqual(200, response.status_code)
        self.assertNotIn(user, response.context["object_list"])
        self.assertNotIn(user2, response.context["object_list"])

    def test_colleges_list(self):
        """Tests the view to list colleges."""

        response = self.client.get(reverse("destinations:colleges"))
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            reverse("authentication:login")
            + f"?next={reverse('destinations:colleges')}",
            response.url,
        )

        user = self.login(make_student=True, accept_tos=True, make_senior=True)

        # Delete all the decisions
        Decision.objects.all().delete()
        College.objects.all().delete()

        # Load the page
        response = self.client.get(reverse("destinations:colleges"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, response.context["object_list"].count())

        # Add a decision, try again
        college = College.objects.get_or_create(
            name="test college", location="Arlington, VA"
        )[0]
        Decision.objects.get_or_create(
            college=college, user=user, decision_type="ED", admission_status="ADMIT"
        )

        response = self.client.get(reverse("destinations:colleges"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            0, response.context["object_list"].count()
        )  # because data not public

        user.publish_data = True
        user.save()

        response = self.client.get(reverse("destinations:colleges"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context["object_list"].count())
        self.assertIn(college, response.context["object_list"])
        self.assertEqual(1, response.context["object_list"][0].count_decisions)
        self.assertEqual(0, response.context["object_list"][0].count_attending)
        self.assertEqual(1, response.context["object_list"][0].count_admit)
        self.assertEqual(0, response.context["object_list"][0].count_waitlist)
        self.assertEqual(0, response.context["object_list"][0].count_waitlist_admit)
        self.assertEqual(0, response.context["object_list"][0].count_waitlist_deny)
        self.assertEqual(0, response.context["object_list"][0].count_defer)
        self.assertEqual(0, response.context["object_list"][0].count_defer_admit)
        self.assertEqual(0, response.context["object_list"][0].count_defer_deny)
        self.assertEqual(0, response.context["object_list"][0].count_defer_wl)
        self.assertEqual(0, response.context["object_list"][0].count_defer_wl_admit)
        self.assertEqual(0, response.context["object_list"][0].count_defer_wl_deny)
        self.assertEqual(0, response.context["object_list"][0].count_deny)

        # Add another decision under a different user but the same college
        user2 = self.login(
            username="2021awilliam",
            make_student=True,
            accept_tos=True,
            make_senior=True,
            publish_data=True,
        )
        decision = Decision.objects.get_or_create(
            college=college,
            user=user2,
            decision_type="ED",
            admission_status="WAITLIST_DENY",
        )[0]

        response = self.client.get(reverse("destinations:colleges"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context["object_list"].count())
        self.assertIn(college, response.context["object_list"])
        self.assertEqual(0, response.context["object_list"][0].count_attending)
        self.assertEqual(2, response.context["object_list"][0].count_decisions)
        self.assertEqual(1, response.context["object_list"][0].count_admit)
        self.assertEqual(0, response.context["object_list"][0].count_waitlist)
        self.assertEqual(0, response.context["object_list"][0].count_waitlist_admit)
        self.assertEqual(1, response.context["object_list"][0].count_waitlist_deny)
        self.assertEqual(0, response.context["object_list"][0].count_defer)
        self.assertEqual(0, response.context["object_list"][0].count_defer_admit)
        self.assertEqual(0, response.context["object_list"][0].count_defer_deny)
        self.assertEqual(0, response.context["object_list"][0].count_defer_wl)
        self.assertEqual(0, response.context["object_list"][0].count_defer_wl_admit)
        self.assertEqual(0, response.context["object_list"][0].count_defer_wl_deny)
        self.assertEqual(0, response.context["object_list"][0].count_deny)

        # make user2 attend this college
        user2.attending_decision = decision
        user2.save()

        response = self.client.get(reverse("destinations:colleges"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context["object_list"].count())
        self.assertIn(college, response.context["object_list"])
        self.assertEqual(1, response.context["object_list"][0].count_attending)
        self.assertEqual(2, response.context["object_list"][0].count_decisions)
        self.assertEqual(1, response.context["object_list"][0].count_admit)
        self.assertEqual(0, response.context["object_list"][0].count_waitlist)
        self.assertEqual(0, response.context["object_list"][0].count_waitlist_admit)
        self.assertEqual(1, response.context["object_list"][0].count_waitlist_deny)
        self.assertEqual(0, response.context["object_list"][0].count_defer)
        self.assertEqual(0, response.context["object_list"][0].count_defer_admit)
        self.assertEqual(0, response.context["object_list"][0].count_defer_deny)
        self.assertEqual(0, response.context["object_list"][0].count_defer_wl)
        self.assertEqual(0, response.context["object_list"][0].count_defer_wl_admit)
        self.assertEqual(0, response.context["object_list"][0].count_defer_wl_deny)
        self.assertEqual(0, response.context["object_list"][0].count_deny)

        # Add another decision for user2 under a different college
        college2 = College.objects.get_or_create(
            name="university of test", location="Alexandria, VA"
        )[0]
        Decision.objects.get_or_create(
            college=college2, user=user2, decision_type="RD", admission_status="DENY"
        )

        response = self.client.get(reverse("destinations:colleges"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, response.context["object_list"].count())

        # Test filtering
        response = self.client.get(reverse("destinations:colleges"), data={"q": "VA"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, response.context["object_list"].count())
        self.assertIn(college, response.context["object_list"])
        self.assertIn(college2, response.context["object_list"])

        response = self.client.get(reverse("destinations:colleges"), data={"q": "1234"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context["object_list"].count())
        self.assertIn(college2, response.context["object_list"])

    def test_import_ceeb_command(self):
        # First, just call the command
        with self.assertRaises(CommandError):
            call_command("import_ceeb")

        College.objects.all().delete()

        file_contents = (
            "CEEB,College Name,City,State\n"
            "1234,Test University,Alexandria,VA\n"
            "1235,University of Test,Arlington,VA\n"
            "INTL,University of Abroad,ExampleCity,RANDOMCOUNTRY"
        )
        with patch(
            "tjdests.apps.destinations.management.commands.import_ceeb.open",
            mock_open(read_data=file_contents),
        ) as mock_obj:
            call_command("import_ceeb", "foo.csv")

        mock_obj.assert_called_with("foo.csv", "r", encoding="utf-8")

        self.assertEqual(
            1,
            College.objects.filter(
                name="Test University", location="Alexandria, VA"
            ).count(),
        )
        self.assertEqual(
            1,
            College.objects.filter(
                name="University of Test", location="Arlington, VA"
            ).count(),
        )
        self.assertEqual(
            1,
            College.objects.filter(
                name="University of Abroad",
                location="ExampleCity, RANDOMCOUNTRY",
            ).count(),
        )

        # Doing it again should have no duplicates
        # But let's add a few more...

        file_contents = (
            "CEEB,College Name,City,State\n"
            "1234,Test University,Alexandria,VA\n"
            "1235,University of Test,Arlington,VA\n"
            "INTL,University of Abroad,ExampleCity,RANDOMCOUNTRY\n"
            "INTL,University of Abroad in CityTwo,CityTwo,RANDOMCOUNTRY\n"
        )

        with patch(
            "tjdests.apps.destinations.management.commands.import_ceeb.open",
            mock_open(read_data=file_contents),
        ) as mock_obj:
            call_command("import_ceeb", "foo.csv")

        mock_obj.assert_called_with("foo.csv", "r", encoding="utf-8")

        self.assertEqual(
            1,
            College.objects.filter(
                name="Test University", location="Alexandria, VA"
            ).count(),
        )
        self.assertEqual(
            1,
            College.objects.filter(
                name="University of Test", location="Arlington, VA"
            ).count(),
        )
        self.assertEqual(
            1,
            College.objects.filter(
                name="University of Abroad",
                location="ExampleCity, RANDOMCOUNTRY",
            ).count(),
        )
        self.assertEqual(
            1,
            College.objects.filter(
                name="University of Abroad in CityTwo",
                location="CityTwo, RANDOMCOUNTRY",
            ).count(),
        )
