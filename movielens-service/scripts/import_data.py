#!/usr/bin/env python3
"""
Import MovieLens CSV data into PostgreSQL.

Usage
-----
  python import_data.py --data-dir /path/to/ml-latest-small

Expected files inside *data_dir*:
  - movies.csv   (movieId,title,genres)
  - ratings.csv  (userId,movieId,rating,timestamp)
  - tags.csv     (userId,movieId,tag,timestamp)   [optional]

Environment variables (or .env file):
  DATABASE_URL – e.g. postgresql://postgres:postgres@localhost:5432/movielens
"""

import argparse
import csv
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/movielens")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def import_movies(cur, data_dir: Path):
    path = data_dir / "movies.csv"
    print(f"Importing movies from {path} …")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [(int(r["movieId"]), r["title"], r["genres"]) for r in reader]
    cur.executemany(
        """
        INSERT INTO movies (movie_id, title, genres)
        VALUES (%s, %s, %s)
        ON CONFLICT (movie_id) DO UPDATE
            SET title  = EXCLUDED.title,
                genres = EXCLUDED.genres
        """,
        rows,
    )
    print(f"  → {len(rows)} movies upserted.")


def import_ratings(cur, data_dir: Path):
    path = data_dir / "ratings.csv"
    print(f"Importing ratings from {path} …")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                int(r["userId"]),
                int(r["movieId"]),
                float(r["rating"]),
                datetime.fromtimestamp(int(r["timestamp"]), tz=timezone.utc),
            )
            for r in reader
        ]
    cur.executemany(
        """
        INSERT INTO ratings (user_id, movie_id, rating, rated_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, movie_id) DO UPDATE
            SET rating   = EXCLUDED.rating,
                rated_at = EXCLUDED.rated_at
        """,
        rows,
    )
    print(f"  → {len(rows)} ratings upserted.")


def import_tags(cur, data_dir: Path):
    path = data_dir / "tags.csv"
    if not path.exists():
        print("  tags.csv not found – skipping.")
        return
    print(f"Importing tags from {path} …")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                int(r["userId"]),
                int(r["movieId"]),
                r["tag"],
                datetime.fromtimestamp(int(r["timestamp"]), tz=timezone.utc),
            )
            for r in reader
        ]
    cur.executemany(
        """
        INSERT INTO tags (user_id, movie_id, tag, tagged_at)
        VALUES (%s, %s, %s, %s)
        """,
        rows,
    )
    print(f"  → {len(rows)} tags inserted.")


def main():
    parser = argparse.ArgumentParser(description="Import MovieLens CSV data into PostgreSQL.")
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory containing movies.csv, ratings.csv and (optionally) tags.csv",
    )
    args = parser.parse_args()
    data_dir = Path(args.data_dir)

    if not data_dir.is_dir():
        raise SystemExit(f"Data directory not found: {data_dir}")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            import_movies(cur, data_dir)
            import_ratings(cur, data_dir)
            import_tags(cur, data_dir)
        conn.commit()
        print("Import complete.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
