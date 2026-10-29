"""Private, explicitly gated Oddize probe policy; not a pick/model endpoint.

RESERVE is intentionally unconfigured. Activation must supply a separately
tested durable, atomic reservation backend with a hard source-call budget.
No in-memory/ephemeral fallback is permitted. Consumed reservations never reset
because a source request failed: retry accounting must remain conservative.
"""
import json
import os
from uuid import UUID
from oddize_capture import capture

RESERVE = None


def enabled():
    return os.environ.get('PICKNOW_ENABLE_ODDIZE_PROBE') == '1'


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate field')
        result[key] = value
    return result


def run(raw):
    """Called only after HTTP origin+owner authentication; never authenticates.

    Budget backend contract: reserve(canonical UUID4) returns 'reserved',
    'already_used' or 'exhausted' after an atomic durable commit. Unknown/error
    means no source call. Replay refuses a new call, rather than retrying.
    """
    base = dict(approved_for_picks=False, training_eligible=False)
    if not enabled():
        return 404, dict(base, status='disabled')
    try:
        payload = json.loads(raw.decode('utf-8'), object_pairs_hook=_object)
        if not isinstance(payload, dict) or set(payload) != {'request_id'}:
            raise ValueError('Invalid schema')
        request_id = payload['request_id']
        if not isinstance(request_id, str) or len(request_id) != 36:
            raise ValueError('Invalid identity')
        value = UUID(request_id)
        if value.version != 4 or str(value) != request_id:
            raise ValueError('Canonical UUID4 required')
    except (ValueError, TypeError, UnicodeError):
        return 400, dict(base, status='invalid_request')
    if not os.environ.get('PICKNOW_ODDIZE_API_KEY', '').strip():
        return 503, dict(base, status='source_not_configured')
    if not callable(RESERVE):
        return 503, dict(base, status='durable_budget_not_configured')
    try:
        reservation = RESERVE(request_id)
    except Exception:
        return 503, dict(base, status='budget_store_unavailable')
    if reservation == 'already_used':
        return 409, dict(base, status='request_already_used')
    if reservation == 'exhausted':
        return 429, dict(base, status='research_budget_exhausted')
    if reservation != 'reserved':
        return 503, dict(base, status='invalid_budget_reservation')
    try:
        result = capture()
        if not isinstance(result, dict):
            raise ValueError('Invalid capture')
        # Collector's allowlisted sports projection is the only public result.
        safe = {k: result[k] for k in ('source', 'status', 'started_at', 'received_at',
                'http_status', 'sha256', 'quota_headers', 'events') if k in result}
        safe.update(base)
        code = 200 if result.get('status') == 'captured_research_only' else 502
        return code, dict(base, status='research_probe_result', request_id=request_id, capture=safe)
    except Exception:
        return 502, dict(base, status='source_capture_failed', request_id=request_id)
