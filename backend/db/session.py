import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VENV_SITE_PACKAGES = [
    PROJECT_ROOT / ".venv" / "Lib" / "site-packages",
    PROJECT_ROOT / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages",
]

for site_packages in VENV_SITE_PACKAGES:
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_PATH = (Path(__file__).resolve().parent / "citylisting.db").resolve()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{DB_PATH}"

try:
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(DATABASE_URL)
except Exception as exc:
    raise RuntimeError(
        f"Unable to create SQLAlchemy engine for {DATABASE_URL!r} using {sys.executable}."
    ) from exc

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
