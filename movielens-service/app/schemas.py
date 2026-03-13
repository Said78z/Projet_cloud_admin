from typing import List, Optional

from pydantic import BaseModel


class Movie(BaseModel):
    movie_id: int
    title: str
    genres: str

    class Config:
        from_attributes = True


class MovieDetail(Movie):
    avg_rating: Optional[float] = None
    num_ratings: Optional[int] = None


class TopRatedMovie(BaseModel):
    movie_id: int
    title: str
    genres: str
    avg_rating: float
    num_ratings: int


class GenreStats(BaseModel):
    genre: str
    num_movies: int
    avg_rating: Optional[float] = None


class HealthResponse(BaseModel):
    status: str
    database: str
    cache: str
