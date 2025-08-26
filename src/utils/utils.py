import re


def plural_text(zero: str, one: str, many: str, count: int) -> str:
    if count == 0:
        return zero

    if count == 1:
        return one

    return many


def get_homepage_url(extension):
    """
    Retrieve and normalize the homepage URL from the extension preferences.

    This function looks up the `api_url` key inside the extension's preferences,
    trims whitespace, and removes any trailing slashes. If the value is missing
    or empty, it returns an empty string.

    Args:
        extension: Ulauncher extension instance with preferences.

    Returns:
        str: The normalized homepage URL, or an empty string if not set.
    """
    url = extension.preferences.get("api_url").strip()
    return url.rstrip("/") if url else ""


def is_valid_homepage_url(extension):
    url = get_homepage_url(extension)
    url_regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    if not isinstance(url, str) or not url:
        return False

    if re.match(url_regex, url) is None:
        return False

    return True
