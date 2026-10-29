"""Offline create-once forecast journal. Not externally witnessed immutability.

SQLite uniqueness prevents overwrites through this API. SHA256 checks require
an independently retained receipt: a database owner can rewrite both payload
and stored digest. Local clock integrity and source verification are external
requirements. No outcomes, credentials or live selections belong here.
"""
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import math
import sqlite3
from feature_admission import admit_features
from forecast_scoring import probabilities
from evaluation_split import timestamp


PREDICTION_FIELDS = frozenset(('decision_id', 'candidate_version', 'baseline_version',
                              'model_frozen_at', 'candidate_home', 'candidate_away',
                              'baseline_home', 'baseline_away'))


def utc_now():
    return datetime.now(timezone.utc)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def append_forecast(path, observation, prediction, *, evidence_registry=None):
    """Recompute admission, write once, return receipt AFTER commit.

    The receipt (including commit time and digest) must be saved separately.
    Losing it makes the row unusable by read_forecast. Production persistence
    is not configured by this utility; :memory: databases are disallowed.
    """
    if str(path) == ':memory:':
        raise ValueError('A file-backed research journal is required')
    features = admit_features(observation, evidence_registry=evidence_registry)
    if features['status'] != 'research_features_only':
        raise ValueError('Observation failed admission')
    if not isinstance(prediction, dict) or set(prediction) != PREDICTION_FIELDS:
        raise ValueError('Forecast-only schema required')
    for key in ('decision_id', 'candidate_version', 'baseline_version'):
        if not isinstance(prediction[key], str) or not prediction[key].strip():
            raise ValueError('Decision and model versions required')
    decision = timestamp(features['decision_at'])
    if timestamp(prediction['model_frozen_at']) > decision:
        raise ValueError('Model frozen after decision')
    for model in ('candidate', 'baseline'):
        home = probabilities(prediction[model+'_home'])
        away = probabilities(prediction[model+'_away'])
        if any(not math.isclose(a, b, rel_tol=0, abs_tol=1e-9)
               for a, b in zip(away, (home[1], home[0], home[2]))):
            raise ValueError('Side probabilities disagree')
    with closing(sqlite3.connect(path, timeout=5)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS forecasts (event TEXT NOT NULL, decision TEXT NOT NULL, '
                   'payload TEXT NOT NULL, digest TEXT NOT NULL, PRIMARY KEY(event, decision))')
        db.execute('BEGIN IMMEDIATE')
        now = utc_now()
        if not 0 <= (now-decision).total_seconds() <= 30:
            raise ValueError('Decision is future or stale at journal insertion')
        envelope = dict(schema_version=1, inserted_at=now.isoformat(), features=features,
                        prediction=prediction)
        payload = encode(envelope)
        digest = hashlib.sha256(payload.encode()).hexdigest()
        try:
            db.execute('INSERT INTO forecasts VALUES (?, ?, ?, ?)',
                       (features['canonical_event_id'], prediction['decision_id'], payload, digest))
            db.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError('Decision already journaled; overwrite refused') from exc
    return dict(canonical_event_id=features['canonical_event_id'], decision_id=prediction['decision_id'],
                sha256=digest, persisted_at=utc_now().isoformat(), approved_for_picks=False)


def read_forecast(path, receipt):
    """Verify content against a separately retained receipt and export scorer row.

    Receipt timestamps are not a trusted external time attestation. Caller must
    protect receipts against rewriting alongside the database.
    """
    with closing(sqlite3.connect(f'file:{path}?mode=ro', uri=True)) as db:
        row = db.execute('SELECT payload, digest FROM forecasts WHERE event=? AND decision=?',
                         (receipt['canonical_event_id'], receipt['decision_id'])).fetchone()
    if row is None:
        raise ValueError('Forecast not found')
    payload, stored = row
    actual = hashlib.sha256(payload.encode()).hexdigest()
    if actual != stored or actual != receipt['sha256']:
        raise ValueError('Forecast digest mismatch')
    envelope = json.loads(payload)
    features, prediction = envelope['features'], envelope['prediction']
    if (features['canonical_event_id'] != receipt['canonical_event_id'] or
            prediction['decision_id'] != receipt['decision_id']):
        raise ValueError('Receipt identity mismatch')
    if not timestamp(features['decision_at']) <= timestamp(envelope['inserted_at']) <= timestamp(receipt['persisted_at']):
        raise ValueError('Receipt chronology invalid')
    return dict(prediction, canonical_event_id=features['canonical_event_id'],
                decision_at=features['decision_at'], persisted_at=receipt['persisted_at'],
                home_line=features['sides']['home']['line'], away_line=features['sides']['away']['line'],
                identity_verified=True, state_verified=True, odds_verified=True,
                forecast_persisted=True, journal_sha256=actual, research_features=features,
                approved_for_picks=False)
