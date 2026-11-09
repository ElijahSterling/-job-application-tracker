"""Database helpers for Elijah Sterling's Job Application Tracker."""
import os
import mysql.connector
from mysql.connector import Error


def get_db():
    """Create a MySQL connection using environment variables."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "job_tracker"),
    )


def query(sql, params=None, fetch="all"):
    """Execute parameterized SQL; return rows or affected-row count."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        if fetch == "all":
            result = cursor.fetchall()
        elif fetch == "one":
            result = cursor.fetchone()
        else:
            result = cursor.lastrowid if fetch == "lastrowid" else cursor.rowcount
        conn.commit()
        return result
    finally:
        cursor.close()
        conn.close()


def json_value(value, default="[]"):
    """Parse JSON from a form field, falling back to a safe JSON string."""
    import json
    if not value:
        return default
    try:
        return json.dumps(json.loads(value))
    except (TypeError, ValueError):
        # Allow comma-separated skill/requirement input as a convenience.
        return json.dumps([part.strip() for part in value.split(",") if part.strip()])
