import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from models import User
from routes.routes import _require_admin_user


def test_require_admin_user_allows_admin_users():
    admin = User(username="admin", email="admin@example.com", password="Password123", is_admin=True)
    assert _require_admin_user(admin) is admin


def test_require_admin_user_rejects_non_admin_users():
    user = User(username="user", email="user@example.com", password="Password123", is_admin=False)
    with pytest.raises(HTTPException) as exc_info:
        _require_admin_user(user)
    assert exc_info.value.status_code == 403
