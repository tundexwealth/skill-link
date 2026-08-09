import os
import sys
import pandas as pd
import sqlite3
import re

BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from db.session import DB_PATH


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    return conn


def _clean_records(records):
    cleaned = []
    for record in records:
        cleaned.append({
            key: None if pd.isna(value) else value
            for key, value in record.items()
        })
    return cleaned


def _format_display_name(value):
    if not value:
        return ""

    parts = []
    for word in str(value).strip().split():
        if re.fullmatch(r"[A-Z]{2,}", word):
            parts.append(word)
        elif re.fullmatch(r"[A-Za-z]{1,3}", word):
            parts.append(word.capitalize())
        else:
            parts.append(word[:1].upper() + word[1:].lower())
    return " ".join(parts)


def _build_search_conditions(query=None, location=None):
    conditions = []
    params = []

    if query:
        query_terms = [term.strip().lower() for term in re.split(r"\s+", query) if term.strip()]
        if query_terms:
            search_field = "LOWER(COALESCE(s.title, '') || ' ' || COALESCE(s.description, '') || ' ' || COALESCE(p.business_name, '') || ' ' || COALESCE(c.name, '') || ' ' || COALESCE(l.area, '') || ' ' || COALESCE(l.city, '') || ' ' || COALESCE(l.state, '') || ' ' || COALESCE(l.address, ''))"
            conditions.extend([f"{search_field} LIKE ?" for _ in query_terms])
            params.extend([f"%{term}%" for term in query_terms])

    if location:
        location_terms = [term.strip().lower() for term in re.split(r"\s+", location) if term.strip()]
        if location_terms:
            location_field = "LOWER(COALESCE(l.area, '') || ' ' || COALESCE(l.city, '') || ' ' || COALESCE(l.state, '') || ' ' || COALESCE(l.address, ''))"
            conditions.extend([f"{location_field} LIKE ?" for _ in location_terms])
            params.extend([f"%{term}%" for term in location_terms])

    return conditions, params


def get_provider_average_rating(provider_id):
    conn = get_connection()
    query = """
    SELECT
        COALESCE(ROUND(AVG(r.score), 1), 0) AS average_rating,
        COUNT(r.id) AS total_ratings
    FROM ratings r
    WHERE r.provider_id = ?
    """
    df = pd.read_sql_query(query, conn, params=[provider_id])
    conn.close()
    result = _clean_records(df.to_dict(orient="records"))
    return result[0] if result else {"average_rating": 0, "total_ratings": 0}

def get_all_ratings_for_provider(provider_id):
    conn = get_connection()
    query = """
    SELECT
        r.id,
        r.score,
        r.comment,
        u.username,
        r.created_at
    FROM ratings r
    LEFT JOIN users u ON r.user_id = u.id
    WHERE r.provider_id = ?
    ORDER BY r.created_at DESC
    """
    df = pd.read_sql_query(query, conn, params=[provider_id])
    conn.close()
    return _clean_records(df.to_dict(orient="records"))


def top_six_services():
    conn = get_connection()
    query = """
        SELECT
            c.id,
            c.name,
            c.image_url,
            COUNT(DISTINCT s.id) AS service_count,
            COALESCE(ROUND(AVG(r.score), 1), 0) AS average_rating,
            COUNT(DISTINCT r.id) AS total_ratings
        FROM categories c
        JOIN services s
            ON c.id = s.category_id
        LEFT JOIN providers p
            ON s.provider_id = p.id
        LEFT JOIN ratings r
            ON p.id = r.provider_id
        GROUP BY c.id, c.name, c.image_url
        ORDER BY service_count DESC
        LIMIT 6
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return _clean_records(df.to_dict(orient="records"))

def categories(type=None):
    conn = get_connection()
    query = """
    SELECT id, name, image_url, description, COUNT(*) AS demand
    FROM categories
    """
    
    normalized_type = type.lower() if type else None
    
    if normalized_type == "home":
        query += " WHERE name IN ('Plumbing', 'Electrical', 'Cleaning', 'Air Conditioner Repair', 'Furniture Repair', 'Generator Repair', 'Home Painting', 'Moving Services', 'Laundry', 'Hair Styling', 'Makeup Artist')"
    elif normalized_type == "education":
        query += " WHERE name IN ('Tutoring', 'Music Lessons', 'Language Classes', 'Art Classes', 'Dance Classes', 'Test Preparation')"
    elif normalized_type == "professional":
        query += " WHERE name IN ('Security Services', 'Event Planning', 'Catering', 'Car Repair', 'Phone Repair', 'Computer Repair', 'Interior Design')"
    elif normalized_type == "creative":
        query += " WHERE name IN ('Photography', 'Videography', 'Graphic Design', 'Web Design', 'Content Creation')"
    else:
        type = None  # Reset type if it doesn't match any category
    
    query += """
    GROUP BY name
    ORDER BY demand DESC
    """
    
        
    df = pd.read_sql_query(query, conn)
    conn.close()
    return _clean_records(df.to_dict(orient="records"))


def services_display(category_id, page=None, page_size=None, query=None, location=None):
    conn = get_connection()
    base_query = """
    WITH unique_services AS (
        SELECT category_id, title, MIN(id) AS min_id
        FROM services
        GROUP BY category_id, title
    )
    SELECT
        s.id,
        s.title,
        s.image_url,
        s.price,
        s.description,
        s.provider_id,
        l.area AS location_name,
        l.city AS location_city,
        l.state AS location_state,
        l.address AS location_address,
        p.phone AS provider_phone,
        p.business_name AS provider_name,
        p.verified AS provider_verified,
        c.name AS category_name,
        COALESCE(ROUND(AVG(r.score), 1), 0) AS average_rating,
        COUNT(DISTINCT r.id) AS total_ratings
    FROM services s
    JOIN unique_services u ON s.id = u.min_id
    LEFT JOIN locations l ON s.location_id = l.id
    LEFT JOIN providers p ON s.provider_id = p.id
    LEFT JOIN categories c ON s.category_id = c.id
    LEFT JOIN ratings r ON p.id = r.provider_id
    WHERE s.category_id = ?
    """
    params = [category_id]
    conditions, filter_params = _build_search_conditions(query, location)
    if conditions:
        base_query += "\n    AND " + "\n    AND ".join(conditions)
        params.extend(filter_params)
    base_query += "\n    GROUP BY s.id, s.title, s.image_url, s.price, s.description, s.provider_id, l.area, l.city, l.state, l.address, p.phone, p.business_name, c.name"
    base_query += "\n    ORDER BY CASE WHEN COUNT(DISTINCT r.id) = 0 THEN 1 ELSE 0 END ASC, average_rating DESC, total_ratings DESC, s.title COLLATE NOCASE ASC, s.id ASC"

    if page is not None and page_size is not None:
        base_query += "\n    LIMIT ? OFFSET ?"
        params.extend([page_size, (page - 1) * page_size])
    df = pd.read_sql_query(base_query, conn, params=params)
    conn.close()
    records = _clean_records(df.to_dict(orient="records"))
    for record in records:
        if "provider_verified" in record:
            record["provider_verified"] = bool(record["provider_verified"])
        if "provider_name" in record:
            record["provider_name"] = _format_display_name(record["provider_name"])
        if "title" in record:
            record["title"] = _format_display_name(record["title"])
    return records


def total_services_count(category_id, query=None, location=None):
    conn = get_connection()
    base_query = """
    WITH unique_services AS (
        SELECT category_id, title, MIN(id) AS min_id
        FROM services
        GROUP BY category_id, title
    )
    SELECT
        COUNT(*) as total
    FROM services s
    JOIN unique_services u ON s.id = u.min_id
    LEFT JOIN locations l ON s.location_id = l.id
    LEFT JOIN providers p ON s.provider_id = p.id
    LEFT JOIN categories c ON s.category_id = c.id
    WHERE s.category_id = ?
    """
    params = [category_id]
    conditions, filter_params = _build_search_conditions(query, location)
    if conditions:
        base_query += "\n    AND " + "\n    AND ".join(conditions)
        params.extend(filter_params)
    df = pd.read_sql_query(base_query, conn, params=params)
    conn.close()
    result = df.to_dict(orient="records")
    return result[0]["total"] if result else 0


def provider_info(provider_id):
    conn = get_connection()
    query = """
    SELECT
        s.id,
        s.title,
        s.image_url,
        s.description,
        s.price,
        l.address AS location_name,
        p.phone AS provider_phone,
        p.email AS provider_email,
        p.website AS provider_website,
        p.linkedin_url AS provider_linkedin_url,
        p.business_name AS provider_name,
        p.verified AS provider_verified,
        p.is_imported AS provider_is_imported,
        p.imported_from AS provider_imported_from,
        c.name AS category_name,
        l.latitude AS latitude,
        l.longitude AS longitude,
        COALESCE(ROUND(AVG(r.score), 1), 0) AS average_rating,
        COUNT(DISTINCT r.id) AS total_ratings
    FROM services s
    LEFT JOIN locations l ON s.location_id = l.id
    LEFT JOIN providers p ON s.provider_id = p.id
    LEFT JOIN categories c ON s.category_id = c.id
    LEFT JOIN ratings r ON p.id = r.provider_id
    WHERE s.provider_id = ?
    GROUP BY s.id, s.title, s.image_url, s.description, s.price, l.address, l.latitude, l.longitude, p.phone, p.email, p.website, p.linkedin_url, p.business_name, p.is_imported, p.imported_from, c.name;
    """
    df = pd.read_sql_query(query, conn, params=[provider_id])
    conn.close()
    records = _clean_records(df.to_dict(orient="records"))
    for record in records:
        if "provider_verified" in record:
            record["provider_verified"] = bool(record["provider_verified"])
            record["verification_status"] = "verified" if record["provider_verified"] else "unverified"
        if "provider_is_imported" in record:
            record["provider_is_imported"] = bool(record["provider_is_imported"])
        if "provider_name" in record:
            record["provider_name"] = _format_display_name(record["provider_name"])
        if "title" in record:
            record["title"] = _format_display_name(record["title"])
    return records


def check_other_providers(provider_id, page=1, page_size=3):
    conn = get_connection()

    category_query = """
    SELECT DISTINCT category_id
    FROM services
    WHERE provider_id = ?
    """
    category_df = pd.read_sql_query(category_query, conn, params=[provider_id])
    categories = category_df["category_id"].dropna().astype(int).tolist()

    if not categories:
        conn.close()
        return []

    placeholders = ",".join(["?" for _ in categories])
    query = f"""
    WITH related_providers AS (
        SELECT provider_id, MIN(id) AS min_service_id
        FROM services
        WHERE category_id IN ({placeholders})
          AND provider_id != ?
        GROUP BY provider_id
        ORDER BY provider_id
        LIMIT ? OFFSET ?
    )
    SELECT
        p.id,
        p.business_name AS title,
        s.image_url,
        s.description,
        s.price,
        l.address AS location_name,
        p.phone AS provider_phone,
        COALESCE(ROUND(AVG(r.score), 1), 0) AS average_rating,
        COUNT(DISTINCT r.id) AS total_ratings
    FROM related_providers rp
    JOIN services s
        ON s.id = rp.min_service_id
    JOIN providers p
        ON p.id = rp.provider_id
    LEFT JOIN locations l
        ON s.location_id = l.id
    LEFT JOIN ratings r
        ON p.id = r.provider_id
    GROUP BY p.id, p.business_name, s.image_url, s.description, s.price, l.address, p.phone
    """

    params = categories + [provider_id, page_size, (page - 1) * page_size]
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return _clean_records(df.to_dict(orient="records"))

def all_providers_display(page=None, page_size=None, query=None, location=None):
    conn = get_connection()
    base_query = """
    WITH unique_services AS (
        SELECT category_id, title, MIN(id) AS min_id
        FROM services
        GROUP BY category_id, title
    )
    SELECT
        s.id,
        s.title,
        s.image_url,
        s.price,
        s.description,
        s.provider_id,
        l.area AS location_name,
        l.city AS location_city,
        l.state AS location_state,
        l.address AS location_address,
        p.phone AS provider_phone,
        p.business_name AS provider_name,
        p.verified AS provider_verified,
        c.name AS category_name,
        COALESCE(ROUND(AVG(r.score), 1), 0) AS average_rating,
        COUNT(DISTINCT r.id) AS total_ratings
    FROM services s
    JOIN unique_services u ON s.id = u.min_id
    LEFT JOIN locations l ON s.location_id = l.id
    LEFT JOIN providers p ON s.provider_id = p.id
    LEFT JOIN categories c ON s.category_id = c.id
    LEFT JOIN ratings r ON p.id = r.provider_id
    WHERE 1 = 1
    """
    params = []
    conditions, filter_params = _build_search_conditions(query, location)
    if conditions:
        base_query += "\n    AND " + "\n    AND ".join(conditions)
        params.extend(filter_params)
    base_query += "\n    GROUP BY s.id, s.title, s.image_url, s.price, s.description, s.provider_id, l.area, l.city, l.state, l.address, p.phone, p.business_name, c.name"
    base_query += "\n    ORDER BY CASE WHEN COUNT(DISTINCT r.id) = 0 THEN 1 ELSE 0 END ASC, average_rating DESC, total_ratings DESC, s.title COLLATE NOCASE ASC, s.id ASC"

    if page is not None and page_size is not None:
        base_query += "\n    LIMIT ? OFFSET ?"
        params.extend([page_size, (page - 1) * page_size])
    df = pd.read_sql_query(base_query, conn, params=params)
    conn.close()
    records = _clean_records(df.to_dict(orient="records"))
    for record in records:
        if "provider_verified" in record:
            record["provider_verified"] = bool(record["provider_verified"])
        if "provider_name" in record:
            record["provider_name"] = _format_display_name(record["provider_name"])
        if "title" in record:
            record["title"] = _format_display_name(record["title"])
    return records


def total_all_services_count(query=None, location=None):
    conn = get_connection()
    base_query = """
    WITH unique_services AS (
        SELECT category_id, title, MIN(id) AS min_id
        FROM services
        GROUP BY category_id, title
    )
    SELECT
        COUNT(*) AS total
    FROM services s
    JOIN unique_services u ON s.id = u.min_id
    LEFT JOIN locations l ON s.location_id = l.id
    LEFT JOIN providers p ON s.provider_id = p.id
    LEFT JOIN categories c ON s.category_id = c.id
    WHERE 1 = 1
    """
    params = []
    conditions, filter_params = _build_search_conditions(query, location)
    if conditions:
        base_query += "\n    AND " + "\n    AND ".join(conditions)
        params.extend(filter_params)
    df = pd.read_sql_query(base_query, conn, params=params)
    conn.close()
    result = df.to_dict(orient="records")
    return result[0]["total"] if result else 0
