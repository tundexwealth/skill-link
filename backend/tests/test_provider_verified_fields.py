import sqlite3

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import queries


def test_services_display_includes_verified_flag(tmp_path, monkeypatch):
    db_path = tmp_path / "provider_verified_test.db"
    monkeypatch.setattr(queries, "DB_PATH", str(db_path))

    conn = sqlite3.connect(str(db_path))
    conn.executescript(
        """
        CREATE TABLE providers (
            id INTEGER PRIMARY KEY,
            business_name TEXT,
            phone TEXT,
            verified INTEGER
        );
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT,
            image_url TEXT,
            description TEXT
        );
        CREATE TABLE locations (
            id INTEGER PRIMARY KEY,
            area TEXT,
            city TEXT,
            state TEXT,
            address TEXT
        );
        CREATE TABLE services (
            id INTEGER PRIMARY KEY,
            title TEXT,
            image_url TEXT,
            description TEXT,
            price TEXT,
            location_id INTEGER,
            provider_id INTEGER,
            category_id INTEGER
        );
        CREATE TABLE ratings (
            id INTEGER PRIMARY KEY,
            provider_id INTEGER,
            score INTEGER,
            comment TEXT,
            user_id INTEGER,
            created_at TEXT
        );
        """
    )
    conn.execute(
        "INSERT INTO providers (id, business_name, phone, verified) VALUES (1, 'Acme Repairs', '555-0100', 1)"
    )
    conn.execute(
        "INSERT INTO categories (id, name, image_url, description) VALUES (1, 'Plumbing', 'img.png', 'Plumbing services')"
    )
    conn.execute(
        "INSERT INTO locations (id, area, city, state, address) VALUES (1, 'Downtown', 'Lagos', 'Lagos', '10 Main St')"
    )
    conn.execute(
        "INSERT INTO services (id, title, image_url, description, price, location_id, provider_id, category_id) VALUES (1, 'Pipe Repair', 'img.png', 'Fast fix', '100', 1, 1, 1)"
    )
    conn.commit()
    conn.close()

    services = queries.services_display(1)

    assert services[0]["provider_verified"] is True


def test_provider_info_includes_verified_flag(tmp_path, monkeypatch):
    db_path = tmp_path / "provider_info_verified_test.db"
    monkeypatch.setattr(queries, "DB_PATH", str(db_path))

    conn = sqlite3.connect(str(db_path))
    conn.executescript(
        """
        CREATE TABLE providers (
            id INTEGER PRIMARY KEY,
            business_name TEXT,
            phone TEXT,
            verified INTEGER
        );
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT,
            image_url TEXT,
            description TEXT
        );
        CREATE TABLE locations (
            id INTEGER PRIMARY KEY,
            area TEXT,
            city TEXT,
            state TEXT,
            address TEXT
        );
        CREATE TABLE services (
            id INTEGER PRIMARY KEY,
            title TEXT,
            image_url TEXT,
            description TEXT,
            price TEXT,
            location_id INTEGER,
            provider_id INTEGER,
            category_id INTEGER
        );
        CREATE TABLE ratings (
            id INTEGER PRIMARY KEY,
            provider_id INTEGER,
            score INTEGER,
            comment TEXT,
            user_id INTEGER,
            created_at TEXT
        );
        """
    )
    conn.execute(
        "INSERT INTO providers (id, business_name, phone, verified) VALUES (2, 'Bright Services', '555-0200', 1)"
    )
    conn.execute(
        "INSERT INTO categories (id, name, image_url, description) VALUES (2, 'Cleaning', 'img.png', 'Cleaning services')"
    )
    conn.execute(
        "INSERT INTO locations (id, area, city, state, address) VALUES (2, 'Ikeja', 'Lagos', 'Lagos', '20 Main St')"
    )
    conn.execute(
        "INSERT INTO services (id, title, image_url, description, price, location_id, provider_id, category_id) VALUES (2, 'House Cleaning', 'img.png', 'Sparkle', '200', 2, 2, 2)"
    )
    conn.commit()
    conn.close()

    services = queries.provider_info(2)

    assert services[0]["provider_verified"] is True
