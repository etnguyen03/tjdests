from decimal import Decimal

from django.urls import reverse

from tjdests.apps.authentication.models import User
from tjdests.apps.destinations.models import College, Decision, TestScore
from tjdests.test import TJDestsTestCase


class ProfileTest(TJDestsTestCase):
    """Tests for the Profile app."""

    def test_profile_view(self):
        """Tests views.profile_view."""

        # Test as an unauthenticated user.
        response = self.client.get(reverse("profile:index"))
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            reverse("authentication:login") + f"?next={reverse('profile:index')}",
            response.url,
        )

        # Test as a user that hasn't accepted TOS.
        self.login(accept_tos=False, make_student=True)
        response = self.client.get(reverse("profile:index"))
        self.assertEqual(302, response.status_code)
        self.assertEqual(reverse("authentication:tos"), response.url)

        # Test as a user that has accepted TOS
        user = self.login(accept_tos=True, make_student=True)
        response = self.client.get(reverse("profile:index"))
        self.assertEqual(200, response.status_code)

        # POST submit the profile form
        response = self.client.post(
            reverse("profile:index"),
            data={
                "GPA": 4.000,
                "biography": "hello",
                "attending_decision": "",
                "publish_data": False,
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            1,
            User.objects.filter(
                GPA=Decimal(4.000),
                id=user.id,
                biography="hello",
                attending_decision=None,
                publish_data=False,
            ).count(),
        )

        response = self.client.post(
            reverse("profile:index"),
            data={
                "biography": "sdf",
                "attending_decision": "",
                "publish_data": False,
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            1,
            User.objects.filter(
                GPA=None,
                id=user.id,
                biography="sdf",
                attending_decision=None,
                publish_data=False,
            ).count(),
        )

        # Test creating an admitted decision, then setting that as our destination.
        college = College.objects.get_or_create(name="test college")[0]
        decision = Decision.objects.get_or_create(
            college=college, user=user, decision_type="ED", admission_status="ADMIT"
        )[0]

        response = self.client.post(
            reverse("profile:index"),
            data={
                "GPA": 3.141,
                "biography": "hello2",
                "attending_decision": decision.id,
                "publish_data": True,
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            1,
            User.objects.filter(
                id=user.id,
                GPA=Decimal(3.141),
                biography="hello2",
                attending_decision=decision,
                publish_data=True,
            ).count(),
        )

        # Test creating a non-admit decision, then setting that as our destination
        college2 = College.objects.get_or_create(name="test university of alexandria")[
            0
        ]
        decision2 = Decision.objects.get_or_create(
            college=college2,
            user=user,
            decision_type="ED",
            admission_status=Decision.DEFER_WL_D,
        )[0]
        response = self.client.post(
            reverse("profile:index"),
            data={
                "GPA": 1.234,
                "biography": "hello2",
                "attending_decision": decision2.id,
                "publish_data": True,
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            1,
            User.objects.filter(
                id=user.id,
                GPA=Decimal(3.141),
                biography="hello2",
                attending_decision=decision,
                publish_data=True,
            ).count(),
        )

        # Test nickname/preferred name feature
        user = self.login(accept_tos=True, make_student=True)
        user.first_name = "Dank"
        user.nickname = "Memer"
        # Should use nickname ("Memer") if option set
        user.use_nickname = True
        self.assertEqual("Memer", user.preferred_name)
        # Should use first name ("Dank") if option not set
        user.use_nickname = False
        self.assertEqual("Dank", user.preferred_name)

    def test_testscore_create(self):
        """Tests creating test scores."""

        # Load the page to create a test score
        # First, test seniors only
        self.login(accept_tos=True, make_student=True)
        response = self.client.get(reverse("profile:testscores_add"))
        self.assertEqual(403, response.status_code)

        user = self.login(accept_tos=True, make_student=True, make_senior=True)
        response = self.client.get(reverse("profile:testscores_add"))
        self.assertEqual(200, response.status_code)

        # POST and create a test score
        response = self.client.post(
            reverse("profile:testscores_add"),
            data={"exam_type": "SAT_TOTAL", "exam_score": 1600},
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            1,
            TestScore.objects.filter(
                user=user, exam_type="SAT_TOTAL", exam_score=1600
            ).count(),
        )

        # Test invalid (and valid) test scores
        # Invalid SAT > 1600
        response = self.client.post(
            reverse("profile:testscores_add"),
            data={"exam_type": "SAT_TOTAL", "exam_score": 1700},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            0,
            TestScore.objects.filter(
                user=user, exam_type="SAT_TOTAL", exam_score=1700
            ).count(),
        )

        # Invalid SAT, doesn't mod 10
        response = self.client.post(
            reverse("profile:testscores_add"),
            data={"exam_type": "SAT_TOTAL", "exam_score": 1543},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            0,
            TestScore.objects.filter(
                user=user, exam_type="SAT_TOTAL", exam_score=1543
            ).count(),
        )

        # Valid ACT
        response = self.client.post(
            reverse("profile:testscores_add"),
            data={"exam_type": "ACT_COMP", "exam_score": 5},
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            1,
            TestScore.objects.filter(
                user=user, exam_type="ACT_COMP", exam_score=5
            ).count(),
        )

        # Invalid ACT, > 36
        response = self.client.post(
            reverse("profile:testscores_add"),
            data={"exam_type": "ACT_COMP", "exam_score": 37},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            0,
            TestScore.objects.filter(
                user=user, exam_type="ACT_COMP", exam_score=37
            ).count(),
        )

        # Invalid ACT, not an integer
        response = self.client.post(
            reverse("profile:testscores_add"),
            data={"exam_type": "ACT_COMP", "exam_score": 3.6},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            0,
            TestScore.objects.filter(
                user=user, exam_type="ACT_COMP", exam_score=3.6  # type: ignore
            ).count(),
        )

        # Valid SAT2
        response = self.client.post(
            reverse("profile:testscores_add"),
            data={"exam_type": "SAT2_MATH2", "exam_score": 300},
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            1,
            TestScore.objects.filter(
                user=user, exam_type="SAT2_MATH2", exam_score=300
            ).count(),
        )

        # Invalid SAT2, <200
        response = self.client.post(
            reverse("profile:testscores_add"),
            data={"exam_type": "SAT2_MATH2", "exam_score": 100},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            0,
            TestScore.objects.filter(
                user=user, exam_type="SAT2_MATH2", exam_score=100
            ).count(),
        )

        # Invalid SAT2, doesn't mod 10
        response = self.client.post(
            reverse("profile:testscores_add"),
            data={"exam_type": "SAT2_MATH2", "exam_score": 243},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            0,
            TestScore.objects.filter(
                user=user, exam_type="SAT2_MATH2", exam_score=243
            ).count(),
        )

        # Valid AP
        response = self.client.post(
            reverse("profile:testscores_add"),
            data={"exam_type": "AP_CSA", "exam_score": 5},
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            1,
            TestScore.objects.filter(
                user=user, exam_type="AP_CSA", exam_score=5
            ).count(),
        )

        # Invalid AP, <1
        response = self.client.post(
            reverse("profile:testscores_add"),
            data={"exam_type": "AP_CSA", "exam_score": 0},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            0,
            TestScore.objects.filter(
                user=user, exam_type="AP_CSA", exam_score=0
            ).count(),
        )

        # Invalid AP, not an integer
        response = self.client.post(
            reverse("profile:testscores_add"),
            data={"exam_type": "AP_CSA", "exam_score": 3.6},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            0,
            TestScore.objects.filter(
                user=user, exam_type="AP_CSA", exam_score=3.6  # type: ignore
            ).count(),
        )

    def test_testscore_update(self):
        """Tests the view to update testscores."""

        user = self.login(make_senior=True, make_student=True, accept_tos=True)

        # Create a test score
        testscore = TestScore.objects.get_or_create(
            user=user, exam_type="AP_CSA", exam_score=5
        )[0]

        # Load the page to edit it
        response = self.client.get(
            reverse("profile:testscores_edit", kwargs={"pk": testscore.id})
        )
        self.assertEqual(200, response.status_code)

        # Logging in as someone else should 404
        self.login(
            username="2021awilliam",
            make_student=True,
            make_senior=True,
            accept_tos=True,
        )
        response = self.client.get(
            reverse("profile:testscores_edit", kwargs={"pk": testscore.id})
        )
        self.assertEqual(404, response.status_code)

        self.login(make_senior=True, make_student=True, accept_tos=True)

        # Change the score to a 4
        response = self.client.post(
            reverse("profile:testscores_edit", kwargs={"pk": testscore.id}),
            data={"exam_type": "AP_CSA", "exam_score": 4},
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            1,
            TestScore.objects.filter(
                id=testscore.id, exam_type="AP_CSA", exam_score=4
            ).count(),
        )
        self.assertEqual(
            0,
            TestScore.objects.filter(
                id=testscore.id, exam_type="AP_CSA", exam_score=5
            ).count(),
        )

        # Test invalid score
        response = self.client.post(
            reverse("profile:testscores_edit", kwargs={"pk": testscore.id}),
            data={"exam_type": "AP_CSA", "exam_score": 6},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            1,
            TestScore.objects.filter(
                id=testscore.id, exam_type="AP_CSA", exam_score=4
            ).count(),
        )
        self.assertEqual(
            0,
            TestScore.objects.filter(
                id=testscore.id, exam_type="AP_CSA", exam_score=6
            ).count(),
        )

    def test_testscore_delete(self):
        """Tests the view to delete testscores."""

        user = self.login(make_senior=True, make_student=True, accept_tos=True)

        # Create a test score
        testscore = TestScore.objects.get_or_create(
            user=user, exam_type="AP_CSA", exam_score=5
        )[0]

        # Load the page to delete it
        response = self.client.get(
            reverse("profile:testscores_delete", kwargs={"pk": testscore.id})
        )
        self.assertEqual(200, response.status_code)

        # Logging in as someone else should 404
        self.login(
            username="2021awilliam",
            make_student=True,
            make_senior=True,
            accept_tos=True,
        )
        response = self.client.get(
            reverse("profile:testscores_delete", kwargs={"pk": testscore.id})
        )
        self.assertEqual(404, response.status_code)

        self.login(make_senior=True, make_student=True, accept_tos=True)

        # Delete it
        response = self.client.post(
            reverse("profile:testscores_delete", kwargs={"pk": testscore.id})
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(0, TestScore.objects.filter(id=testscore.id).count())

    def test_decision_create(self):
        """Tests the view to create decisions."""

        user = self.login(make_senior=True, make_student=True, accept_tos=True)

        # Create a college.
        college = College.objects.get_or_create(name="test college")[0]

        # Load the page
        response = self.client.get(reverse("profile:decision_add"))
        self.assertEqual(200, response.status_code)

        # Clear any decisions present
        Decision.objects.all().delete()

        # Add the decision
        response = self.client.post(
            reverse("profile:decision_add"),
            data={
                "college": college.id,
                "decision_type": "RL",  # rolling
                "admission_status": "ADMIT",
            },
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            1,
            Decision.objects.filter(
                college=college,
                user=user,
                decision_type=Decision.ROLLING,
                admission_status=Decision.ADMIT,
            ).count(),
        )

        # Adding another decision of this college should not work
        response = self.client.post(
            reverse("profile:decision_add"),
            data={
                "college": college.id,
                "decision_type": "RD",
                "admission_status": "WAITLIST",
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, Decision.objects.filter(college=college, user=user).count())

        # No deferrals for RD and rolling
        Decision.objects.all().delete()
        response = self.client.post(
            reverse("profile:decision_add"),
            data={
                "college": college.id,
                "decision_type": "RD",
                "admission_status": "DEFER_WAITLIST_ADMIT",
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, Decision.objects.filter(college=college, user=user).count())

        response = self.client.post(
            reverse("profile:decision_add"),
            data={
                "college": college.id,
                "decision_type": "RD",
                "admission_status": "WAITLIST",
            },
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            1,
            Decision.objects.filter(
                college=college, user=user, admission_status=Decision.WAITLIST
            ).count(),
        )

        # Test adding an early-decision decision and receiving admittance
        Decision.objects.all().delete()
        response = self.client.post(
            reverse("profile:decision_add"),
            data={
                "college": college.id,
                "decision_type": "ED",
                "admission_status": "ADMIT",
            },
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            1,
            Decision.objects.filter(
                college=college,
                user=user,
                admission_status=Decision.ADMIT,
                decision_type=Decision.EARLY_DECISION,
            ).count(),
        )
        # The user's attending college should be set to the one just added
        self.assertEqual(
            User.objects.get(id=user.id).attending_decision,
            Decision.objects.get(
                college=college,
                user=user,
                admission_status=Decision.ADMIT,
                decision_type=Decision.EARLY_DECISION,
            ),
        )

    def test_decision_update(self):
        user = self.login(make_senior=True, make_student=True, accept_tos=True)

        # Create a college.
        college = College.objects.get_or_create(name="test college")[0]

        # Clear any decisions present
        Decision.objects.all().delete()

        # Create a decision
        decision = Decision.objects.get_or_create(
            college=college, user=user, decision_type="ED", admission_status="ADMIT"
        )[0]

        # Load the update page
        response = self.client.get(
            reverse("profile:decision_edit", kwargs={"pk": decision.id})
        )
        self.assertEqual(200, response.status_code)

        # Logging in as someone else should 404
        self.login(
            username="2021awilliam",
            make_student=True,
            make_senior=True,
            accept_tos=True,
        )
        response = self.client.get(
            reverse("profile:decision_edit", kwargs={"pk": decision.id})
        )
        self.assertEqual(404, response.status_code)

        self.login(make_senior=True, make_student=True, accept_tos=True)

        # Make an update but don't change the college
        response = self.client.post(
            reverse("profile:decision_edit", kwargs={"pk": decision.id}),
            data={
                "college": college.id,
                "decision_type": "ED",
                "admission_status": "DENY",
            },
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            1,
            Decision.objects.filter(
                college=college,
                user=user,
                decision_type="ED",
                admission_status="DENY",
                id=decision.id,
            ).count(),
        )
        self.assertEqual(
            0,
            Decision.objects.filter(
                college=college, user=user, decision_type="ED", admission_status="ADMIT"
            ).count(),
        )

        # Change the college
        college2 = College.objects.get_or_create(name="University of Test")[0]
        response = self.client.post(
            reverse("profile:decision_edit", kwargs={"pk": decision.id}),
            data={
                "college": college2.id,
                "decision_type": "ED",
                "admission_status": "DENY",
            },
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            1,
            Decision.objects.filter(
                college=college2,
                user=user,
                decision_type="ED",
                admission_status="DENY",
                id=decision.id,
            ).count(),
        )
        self.assertEqual(0, Decision.objects.filter(college=college).count())

        # Add a decision for college (not college2)
        Decision.objects.get_or_create(
            college=college, user=user, decision_type="ED", admission_status="ADMIT"
        )

        # Now, there are two decisions, one for college and one for college2
        # Try to edit the decision for college2 -> college
        decision2 = Decision.objects.get(college=college2, user=user)

        response = self.client.post(
            reverse("profile:decision_edit", kwargs={"pk": decision2.id}),
            data={
                "college": college.id,
                "decision_type": "ED",
                "admission_status": "DENY",
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            1, Decision.objects.filter(college=college2, user=user).count()
        )
        self.assertEqual(1, Decision.objects.filter(college=college, user=user).count())

    def test_decision_delete(self):
        """Tests the view to delete a decision."""

        user = self.login(make_senior=True, make_student=True, accept_tos=True)

        # Create a decision
        college = College.objects.get_or_create(name="test college")[0]
        decision = Decision.objects.get_or_create(
            college=college, user=user, decision_type="ED", admission_status="ADMIT"
        )[0]

        # Load the update page
        response = self.client.get(
            reverse("profile:decision_delete", kwargs={"pk": decision.id})
        )
        self.assertEqual(200, response.status_code)

        # Logging in as someone else should 404
        self.login(
            username="2021awilliam",
            make_student=True,
            make_senior=True,
            accept_tos=True,
        )
        response = self.client.get(
            reverse("profile:decision_delete", kwargs={"pk": decision.id})
        )
        self.assertEqual(404, response.status_code)

        self.login(make_senior=True, make_student=True, accept_tos=True)

        # Delete the decision
        response = self.client.post(
            reverse("profile:decision_delete", kwargs={"pk": decision.id})
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(0, Decision.objects.filter(id=decision.id).count())
