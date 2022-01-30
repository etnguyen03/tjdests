from markdown import markdown

from django import template

from .strikethrough import StrikethroughExtension

register = template.Library()


@register.filter(name="markdown")
def convert_markdown(text: str):
    """Convert text to markdown HTML."""
    return markdown(
        text, extensions=["extra", "codehilite", "smarty", StrikethroughExtension()]
    )
