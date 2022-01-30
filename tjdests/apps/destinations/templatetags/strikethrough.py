# -*- coding: utf-8 -*-
# pylint: skip-file
"""Markdown Strikethrough Extension
Extends the Python-Markdown library to support strikethrough text.
Given the text:
    The molecular composition of water is ~~HCl~~.
Will output:
    <p>The molecular composition of water is <s>HCl</s>.</p>
Based on Markdown Subscript Extension
    :website: https://github.com/jambonrose/markdown_subscript_extension
    :copyright: Copyright 2014-2018 Andrew Pinkham
    :license: Simplified BSD, see LICENSE for details.
This version by Shreyas Mayya.
Pylint was skipped here because python-markdown appears to require
a specific syntax which is at odds with pylint's ruleset.
"""

from __future__ import unicode_literals

from markdown import Extension
from markdown.inlinepatterns import SimpleTagPattern

# match ~~, at least one character that is not ~, and ~~ again
SUBSCRIPT_RE = r"(\~\~)([^(\~)]+)(\~\~)"


def makeExtension(*args, **kwargs):  # noqa: N802
    """Inform Markdown of the existence of the extension."""
    return StrikethroughExtension(*args, **kwargs)


class StrikethroughExtension(Extension):
    """Extension: text between ~~ characters will be struck through."""

    def extendMarkdown(self, md, md_globals):  # noqa: N802
        """Insert 's' pattern before 'not_strong' pattern."""
        md.inlinePatterns.add(
            "strikethrough", SimpleTagPattern(SUBSCRIPT_RE, "s"), "<not_strong"
        )
