-- Indexes for the MovieLens schema
-- Run AFTER schema.sql and data import.

-- Accelerate title search (ILIKE / LOWER)
CREATE INDEX IF NOT EXISTS idx_movies_title_lower ON movies (LOWER(title));

-- Accelerate genre filter
CREATE INDEX IF NOT EXISTS idx_movies_genres ON movies USING gin (to_tsvector('simple', genres));

-- Accelerate lookups of all ratings for a movie (used in AVG / COUNT aggregations)
CREATE INDEX IF NOT EXISTS idx_ratings_movie_id ON ratings (movie_id);

-- Accelerate lookups of all ratings by a user
CREATE INDEX IF NOT EXISTS idx_ratings_user_id ON ratings (user_id);

-- Accelerate tag lookup by movie
CREATE INDEX IF NOT EXISTS idx_tags_movie_id ON tags (movie_id);
