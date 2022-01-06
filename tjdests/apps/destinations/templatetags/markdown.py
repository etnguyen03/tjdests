from markdown import markdown

from django import template

register = template.Library()


@register.filter(name="markdown")
def convert_markdown(text: str):
    """Convert text to markdown HTML."""
    return markdown(text, extensions=["extra", "codehilite", "smarty"])
