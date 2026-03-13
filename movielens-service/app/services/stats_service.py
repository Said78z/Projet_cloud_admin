from typing import List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas


async def get_genre_stats(db: AsyncSession) -> List[schemas.GenreStats]:
    """Return per-genre movie counts and average ratings.

    Because the MovieLens ``genres`` column stores pipe-separated values
    (e.g. ``"Action|Adventure|Sci-Fi"``), we use ``regexp_split_to_table``
    to unnest them before aggregating.
    """
    query = text(
        """
        SELECT
            genre,
            COUNT(DISTINCT m.movie_id)       AS num_movies,
            ROUND(AVG(r.rating)::numeric, 2) AS avg_rating
        FROM movies m,
             regexp_split_to_table(m.genres, '\\|') AS genre
        LEFT JOIN ratings r ON r.movie_id = m.movie_id
        GROUP BY genre
        ORDER BY num_movies DESC
        """
    )
    result = await db.execute(query)
    rows = result.fetchall()
    return [
        schemas.GenreStats(
            genre=r.genre,
            num_movies=r.num_movies,
            avg_rating=float(r.avg_rating) if r.avg_rating is not None else None,
        )
        for r in rows
    ]


async def get_rating_distribution(db: AsyncSession) -> dict:
    """Return the global rating-value distribution {rating: count}."""
    query = text(
        """
        SELECT rating, COUNT(*) AS cnt
        FROM ratings
        GROUP BY rating
        ORDER BY rating
        """
    )
    result = await db.execute(query)
    return {str(row.rating): row.cnt for row in result.fetchall()}
