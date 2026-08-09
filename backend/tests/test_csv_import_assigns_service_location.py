import os
import sys
import tempfile
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

sys.path.insert(0, os.path.join(BACKEND_DIR, "seed"))

import seed
from db.base import Base


def test_csv_import_assigns_location_to_imported_provider_services():
    engine = create_engine("sqlite:///:memory:")
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    original_session_local = seed.SessionLocal
    seed.SessionLocal = TestSession

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "sample_businesses.csv"
            csv_path.write_text(
                "Business Name,Area,City,State,Address\n"
                "Bright Cleaning Co,Ikorodu,Lagos,Lagos,12 Main Street\n",
                encoding="utf-8",
            )

            seed.import_seed_providers_from_csv(str(csv_path))

            session = TestSession()
            try:
                services = session.query(seed.Service).all()
                assert services, "Expected imported provider service to be created"
                assert services[0].location_id is not None
            finally:
                session.close()
    finally:
        seed.SessionLocal = original_session_local
