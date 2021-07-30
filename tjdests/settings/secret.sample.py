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

# Message blast - treated as HTML safe text
# type is str
GLOBAL_MESSAGE = None

# Login lock: if True, restrict login to superusers only
LOGIN_LOCKED = False
