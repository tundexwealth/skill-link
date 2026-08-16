import sys
from datetime import timedelta
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from security import session_has_expired, utc_now


def test_session_expiry_accepts_postgresql_aware_timestamps():
    assert not session_has_expired(utc_now() + timedelta(minutes=1))
    assert session_has_expired(utc_now() - timedelta(minutes=1))


def test_session_expiry_accepts_legacy_sqlite_naive_timestamps():
    assert not session_has_expired((utc_now() + timedelta(minutes=1)).replace(tzinfo=None))
    assert session_has_expired((utc_now() - timedelta(minutes=1)).replace(tzinfo=None))
