"""Validate the optional URL prefix shared by the server and sync client."""
import re

BASE_PATH = re.compile(r'^/[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*$')


def normalize_base_path(value):
    if value in ('', '/'):
        return ''
    if not isinstance(value, str):
        raise ValueError('Base path must be a URL path')
    candidate = value[:-1] if value.endswith('/') else value
    if not BASE_PATH.fullmatch(candidate):
        raise ValueError('Base path must use /segment[/segment] with letters, digits, _ or -')
    return candidate
