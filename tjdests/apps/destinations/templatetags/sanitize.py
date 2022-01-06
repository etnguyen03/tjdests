from bleach import clean
from bleach.sanitizer import ALLOWED_TAGS

from django import template

register = template.Library()

tags = ALLOWED_TAGS + ["h" + str(i) for i in range(1, 7)] + ["div", "p", "pre", "span"]
attrs = {"*": ["class"]}


@register.filter(name="sanitize")
def convert_markdown(text: str):
    """Sanitize HTML (removing potential XSS attacks)."""
    return clean(text, tags=tags, attributes=attrs)
