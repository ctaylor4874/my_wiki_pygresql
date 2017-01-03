import re


def _replace(word):
    return '<a href="/%s">%s</a>' % (word.group(0), word.group(0))


def wiki_linkify(string):
    return re.sub('([A-Z][a-z]+){2,}', _replace, string)
