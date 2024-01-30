from typing import List

# Deployed senior graduation year
# e.g. if deploying in spring 2021, then 2021
SENIOR_GRAD_YEAR = 2021

# Branding name
BRANDING_NAME = "TJ Destinations"

# DEBUG and authorized hosts
DEBUG = True
ALLOWED_HOSTS: List[str] = []

# secret
SECRET_KEY = "supersecret"

# OAuth
SOCIAL_AUTH_ION_KEY = "ionkey"
SOCIAL_AUTH_ION_SECRET = "ionsecret"

# Database
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.environ["DIRECTOR_DATABASE_NAME"],
#         "USER": os.environ["DIRECTOR_DATABASE_USERNAME"],
#         "PASSWORD": os.environ["DIRECTOR_DATABASE_PASSWORD"],
#         "HOST": os.environ["DIRECTOR_DATABASE_HOST"],
#         "PORT": os.environ["DIRECTOR_DATABASE_PORT"],
#     },
# }

# Axes
# AXES_META_PRECEDENCE_ORDER = [
#     'HTTP_X_REAL_IP',
# ]
# AXES_NEVER_LOCKOUT_WHITELIST = True
# AXES_IP_WHITELIST = ["151.188.227.237"]

# Message blast - treated as HTML safe text
# type is str
GLOBAL_MESSAGE = None
# GLOBAL_MESSAGE = "<b>WARNING</b>: This is not ready for production usage! Any and all data may be deleted at any time without warning!"

# Login lock: if True, restrict login to superusers only
LOGIN_LOCKED = False

TIME_ZONE = "America/New_York"

# To prevent Git issues
MAINTAINER = "First Last (20XXusername)"
