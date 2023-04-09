from django.db import models


class College(models.Model):
    """Represents a college."""

    name = models.CharField(max_length=250, null=False, blank=False)
    location = models.CharField(max_length=250, null=False, blank=False)

    def __str__(self):
        return f"{self.name} - {self.location}"

    class Meta:
        ordering = ["name", "location"]


class Decision(models.Model):
    """Represents a college decision."""

    EARLY_DECISION = "ED"
    EARLY_DECISION_2 = "ED2"
    EARLY_ACTION = "EA"
    EARLY_ACTION_2 = "EA2"
    PRIORITY = "PR"
    REGULAR_DECISION = "RD"
    ROLLING = "RL"

    DECISION_TYPE_CHOICES = [
        (EARLY_DECISION, "Early Decision"),
        (EARLY_DECISION_2, "Early Decision 2"),
        (EARLY_ACTION, "Early Action"),
        (EARLY_ACTION_2, "Early Action 2"),
        (PRIORITY, "Priority"),
        (REGULAR_DECISION, "Regular Decision"),
        (ROLLING, "Rolling"),
    ]

    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE)

    decision_type = models.CharField(
        max_length=20, choices=DECISION_TYPE_CHOICES, null=True
    )

    ADMIT = "ADMIT"
    WAITLIST_ADMIT = "WAITLIST_ADMIT"
    WAITLIST_DENY = "WAITLIST_DENY"
    WAITLIST = "WAITLIST"
    DEFER_ADMIT = "DEFER_ADMIT"
    DEFER_DENY = "DEFER_DENY"
    DEFER_WL = "DEFER_WAITLIST"
    DEFER_WL_A = "DEFER_WAITLIST_ADMIT"
    DEFER_WL_D = "DEFER_WAITLIST_DENY"
    DEFER = "DEFER"
    DENY = "DENY"
    UNKNOWN = "UNKNOWN"

    ADMIT_TYPE_CHOICES = [
        (ADMIT, "Admitted"),
        (WAITLIST, "Waitlisted"),
        (WAITLIST_ADMIT, "Waitlist-Admitted"),
        (WAITLIST_DENY, "Waitlist-Denied"),
        (DEFER, "Deferred"),
        (DEFER_ADMIT, "Deferred-Admitted"),
        (DEFER_DENY, "Deferred-Denied"),
        (DEFER_WL, "Deferred-Waitlisted"),
        (DEFER_WL_A, "Deferred-Waitlisted-Admitted"),
        (DEFER_WL_D, "Deferred-Waitlisted-Denied"),
        (DENY, "Denied"),
        (UNKNOWN, "Unknown"),
    ]

    admission_status = models.CharField(max_length=20, choices=ADMIT_TYPE_CHOICES)
    college = models.ForeignKey(College, on_delete=models.CASCADE)

    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["admission_status", "college"]

    def __str__(self):
        return (
            f"{self.college.name} - {self.get_decision_type_display()}: "
            f"{self.get_admission_status_display()}"
        )


class TestScore(models.Model):
    """Represents a test score."""

    # Test score types for validation purposes
    ACT_ENGL = "ACT_ENGL"
    ACT_MATH = "ACT_MATH"
    ACT_READ = "ACT_READ"
    ACT_SCI = "ACT_SCI"
    ACT_COMP = "ACT_COMP"

    # SAT
    SAT_EBRW = "SAT_EBRW"
    SAT_MATH = "SAT_MATH"
    SAT_TOTAL = "SAT_TOTAL"

    # SAT Subject Tests
    SAT2_MATH1 = "SAT2_MATH1"
    SAT2_MATH2 = "SAT2_MATH2"
    SAT2_BIO = "SAT2_BIO"
    SAT2_CHEM = "SAT2_CHEM"
    SAT2_PHYS = "SAT2_PHYS"
    SAT2_ENGL = "SAT2_ENGL"
    SAT2_USH = "SAT2_USH"
    SAT2_WH = "SAT2_WH"
    SAT2_ES = "SAT2_ES"
    SAT2_ESL = "SAT2_ESL"
    SAT2_FR = "SAT2_FR"
    SAT2_FRL = "SAT2_FRL"
    SAT2_ZHL = "SAT2_ZHL"
    SAT2_IT = "SAT2_IT"
    SAT2_DE = "SAT2_DE"
    SAT2_DEL = "SAT2_DEL"
    SAT2_HE = "SAT2_HE"
    SAT2_LA = "SAT2_LA"
    SAT2_JAL = "SAT2_JAL"
    SAT2_KOL = "SAT2_KOL"

    # AP Exams
    AP_RSRCH = "AP_RSRCH"
    AP_SMNR = "AP_SMNR"
    AP_ART2D = "AP_ART2D"
    AP_ART3D = "AP_ART3D"
    AP_ARTDRAW = "AP_ARTDRAW"
    AP_ARTHIST = "AP_ARTHIST"
    AP_BIO = "AP_BIO"
    AP_CALCAB = "AP_CALCAB"
    AP_CALCBC = "AP_CALCBC"
    AP_CHEM = "AP_CHEM"
    AP_ZHLANG = "AP_ZHLANG"
    AP_CSA = "AP_CSA"
    AP_CSP = "AP_CSP"
    AP_ENLANG = "AP_ENLANG"
    AP_ENLIT = "AP_ENLIT"
    AP_ENVSCI = "AP_ENVSCI"
    AP_EUROHIST = "AP_EUROHIST"
    AP_FRLANG = "AP_FRLANG"
    AP_DELANG = "AP_DELANG"
    AP_GOVCOMP = "AP_GOVCOMP"
    AP_GOVUS = "AP_GOVUS"
    AP_HUG = "AP_HUG"
    AP_ITLANG = "AP_ITLANG"
    AP_JALANG = "AP_JALANG"
    AP_LATIN = "AP_LATIN"
    AP_MACRO = "AP_MACRO"
    AP_MICRO = "AP_MICRO"
    AP_MUSTHRY = "AP_MUSTHRY"
    AP_PHYSICS1 = "AP_PHYSICS1"
    AP_PHYSICS2 = "AP_PHYSICS2"
    AP_PHYSICSCEM = "AP_PHYSICSCEM"
    AP_PHYSICSCM = "AP_PHYSICSCM"
    AP_PSYCH = "AP_PSYCH"
    AP_ESLANG = "AP_ESLANG"
    AP_ESLIT = "AP_ESLIT"
    AP_STAT = "AP_STAT"
    AP_USH = "AP_USH"
    AP_WHM = "AP_WHM"

    TEST_TYPES = [
        (ACT_ENGL, "ACT English (Grammar)"),
        (ACT_MATH, "ACT Math"),
        (ACT_READ, "ACT Reading"),
        (ACT_SCI, "ACT Science"),
        (ACT_COMP, "ACT Composite"),
        (SAT_EBRW, "SAT Verbal"),
        (SAT_MATH, "SAT Math"),
        (SAT_TOTAL, "SAT Total"),
        (SAT2_MATH1, "SAT Subject Test Math 1"),
        (SAT2_MATH2, "SAT Subject Test Math 2"),
        (SAT2_BIO, "SAT Subject Test Biology"),
        (SAT2_CHEM, "SAT Subject Test Chemistry"),
        (SAT2_PHYS, "SAT Subject Test Physics"),
        (SAT2_ENGL, "SAT Subject Test English"),
        (SAT2_USH, "SAT Subject Test U.S. History"),
        (SAT2_WH, "SAT Subject Test World History"),
        (SAT2_ES, "SAT Subject Test Spanish"),
        (SAT2_ESL, "SAT Subject Test Spanish with Listening"),
        (SAT2_FR, "SAT Subject Test French"),
        (SAT2_FRL, "SAT Subject Test French with Listening"),
        (SAT2_ZHL, "SAT Subject Test Chinese with Listening"),
        (SAT2_IT, "SAT Subject Test Italian"),
        (SAT2_DE, "SAT Subject Test German"),
        (SAT2_DEL, "SAT Subject Test German with Listening"),
        (SAT2_HE, "SAT Subject Test Modern Hebrew"),
        (SAT2_LA, "SAT Subject Test Latin"),
        (SAT2_JAL, "SAT Subject Test Japanese with Listening"),
        (SAT2_KOL, "SAT Subject Test Korean with Listening"),
        (AP_RSRCH, "AP Research"),
        (AP_SMNR, "AP Seminar"),
        (AP_ART2D, "AP Art and Design: 2-D Design"),
        (AP_ART3D, "AP Art and Design: 3-D Design"),
        (AP_ARTDRAW, "AP Art and Design: Drawing"),
        (AP_ARTHIST, "AP Art History"),
        (AP_BIO, "AP Biology"),
        (AP_CALCAB, "AP Calculus AB"),
        (AP_CALCBC, "AP Calculus BC"),
        (AP_CHEM, "AP Chemistry"),
        (AP_ZHLANG, "AP Chinese Language and Culture"),
        (AP_CSA, "AP Computer Science A"),
        (AP_CSP, "AP Computer Science Principles"),
        (AP_ENLANG, "AP English Language and Composition"),
        (AP_ENLIT, "AP English Literature and Composition"),
        (AP_ENVSCI, "AP Environmental Science"),
        (AP_EUROHIST, "AP European History"),
        (AP_FRLANG, "AP French Language and Culture"),
        (AP_DELANG, "AP German Language and Culture"),
        (AP_GOVCOMP, "AP Comparative Government and Politics"),
        (AP_GOVUS, "AP U.S. Government and Politics"),
        (AP_HUG, "AP Human Geography"),
        (AP_ITLANG, "AP Italian Language and Culture"),
        (AP_JALANG, "AP Japanese Language and Culture"),
        (AP_LATIN, "AP Latin"),
        (AP_MACRO, "AP Macroeconomics"),
        (AP_MICRO, "AP Microeconomics"),
        (AP_MUSTHRY, "AP Music Theory"),
        (AP_PHYSICS1, "AP Physics 1: Algebra-Based"),
        (AP_PHYSICS2, "AP Physics 2: Algebra-Based"),
        (AP_PHYSICSCEM, "AP Physics C: Electricity and Magnetism"),
        (AP_PHYSICSCM, "AP Physics C: Mechanics"),
        (AP_PSYCH, "AP Psychology"),
        (AP_ESLANG, "AP Spanish Language and Culture"),
        (AP_ESLIT, "AP Spanish Literature and Culture"),
        (AP_STAT, "AP Statistics"),
        (AP_USH, "AP US History"),
        (AP_WHM, "AP World History: Modern"),
    ]

    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE)

    exam_type = models.CharField(max_length=20, choices=TEST_TYPES, null=False)
    exam_score = models.PositiveSmallIntegerField(null=False)

    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_exam_type_display()}: {self.exam_score}"
