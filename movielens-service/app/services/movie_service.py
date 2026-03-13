from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas


async def search_movies(
    db: AsyncSession,
    title: Optional[str] = None,
    genre: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> List[schemas.Movie]:
    """Return movies filtered by *title* (ILIKE) and/or *genre*."""
    offset = (page - 1) * page_size
    conditions = []
    params: dict = {"limit": page_size, "offset": offset}

    if title:
        conditions.append("LOWER(m.title) LIKE LOWER(:title)")
        params["title"] = f"%{title}%"

    if genre:
        conditions.append("m.genres ILIKE :genre")
        params["genre"] = f"%{genre}%"

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    query = text(
        f"""
        SELECT m.movie_id, m.title, m.genres
        FROM movies m
        {where_clause}
        ORDER BY m.title
        LIMIT :limit OFFSET :offset
        """
    )

    result = await db.execute(query, params)
    rows = result.fetchall()
    return [schemas.Movie(movie_id=r.movie_id, title=r.title, genres=r.genres) for r in rows]


async def get_movie_detail(
    db: AsyncSession,
    movie_id: int,
) -> Optional[schemas.MovieDetail]:
    """Return full detail (including rating stats) for a single movie."""
    query = text(
        """
        SELECT
            m.movie_id,
            m.title,
            m.genres,
            ROUND(AVG(r.rating)::numeric, 2) AS avg_rating,
            COUNT(r.rating)                  AS num_ratings
        FROM movies m
        LEFT JOIN ratings r ON r.movie_id = m.movie_id
        WHERE m.movie_id = :movie_id
        GROUP BY m.movie_id, m.title, m.genres
        """
    )
    result = await db.execute(query, {"movie_id": movie_id})
    row = result.fetchone()
    if row is None:
        return None
    return schemas.MovieDetail(
        movie_id=row.movie_id,
        title=row.title,
        genres=row.genres,
        avg_rating=float(row.avg_rating) if row.avg_rating is not None else None,
        num_ratings=row.num_ratings,
    )


async def get_top_rated(
    db: AsyncSession,
    limit: int = 10,
    min_ratings: int = 50,
) -> List[schemas.TopRatedMovie]:
    """Return the *limit* highest-rated movies that have at least *min_ratings*."""
    query = text(
        """
        SELECT
            m.movie_id,
            m.title,
            m.genres,
            ROUND(AVG(r.rating)::numeric, 2) AS avg_rating,
            COUNT(r.rating)                  AS num_ratings
        FROM movies m
        JOIN ratings r ON r.movie_id = m.movie_id
        GROUP BY m.movie_id, m.title, m.genres
        HAVING COUNT(r.rating) >= :min_ratings
        ORDER BY avg_rating DESC, num_ratings DESC
        LIMIT :limit
        """
    )
    result = await db.execute(query, {"limit": limit, "min_ratings": min_ratings})
    rows = result.fetchall()
    return [
        schemas.TopRatedMovie(
            movie_id=r.movie_id,
            title=r.title,
            genres=r.genres,
            avg_rating=float(r.avg_rating),
            num_ratings=r.num_ratings,
        )
        for r in rows
    ]
