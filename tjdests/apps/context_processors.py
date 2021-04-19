from django.conf import settings


def settings_renderer(request):
    return {"settings": settings}
