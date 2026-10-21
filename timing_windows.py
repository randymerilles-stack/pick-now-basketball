"""Offline protocol windows. Call only with independently verified time inputs.

This helper does not verify source semantics or qualify a prediction.
"""
import math


def timing_window(remaining_seconds, regulation_seconds, *, semantics_verified=False,
                  overtime=False):
    if semantics_verified is not True or overtime is not False:
        return None
    values = (remaining_seconds, regulation_seconds)
    if any(type(x) not in (int, float) or not math.isfinite(x) for x in values):
        return None
    if regulation_seconds <= 0 or not 0 <= remaining_seconds <= regulation_seconds:
        return None
    fraction = remaining_seconds / regulation_seconds
    if fraction < .25:
        return 'remaining_0_25'
    if fraction < .50:
        return 'remaining_25_50'
    if fraction < .75:
        return 'remaining_50_75'
    return 'remaining_75_100'
