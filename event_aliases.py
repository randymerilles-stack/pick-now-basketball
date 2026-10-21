"""Conservative provider-declared event aliases; not independent verification."""


def provider_aliases(requested_id, response):
    """Validate an explicit /closing alias declaration without name inference."""
    valid = lambda value: isinstance(value, str) and value.isascii() and value.isdigit()
    if not valid(requested_id) or not isinstance(response, dict):
        return None
    aliases = response.get('fixture_ids')
    if not isinstance(aliases, list) or not aliases or not all(valid(x) for x in aliases):
        return None
    if len(set(aliases)) != len(aliases) or requested_id not in aliases:
        return None
    if response.get('fixture_id') not in aliases:
        return None
    prematch = response.get('prematch_id')
    if prematch is not None and prematch not in aliases:
        return None
    return tuple(sorted(aliases))
