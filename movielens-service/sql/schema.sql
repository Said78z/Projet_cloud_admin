-- MovieLens database schema
-- Tables mirror the standard MovieLens CSV export format.

CREATE TABLE IF NOT EXISTS movies (
    movie_id   INTEGER PRIMARY KEY,
    title      TEXT    NOT NULL,
    genres     TEXT    NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS ratings (
    user_id    INTEGER NOT NULL,
    movie_id   INTEGER NOT NULL REFERENCES movies (movie_id),
    rating     NUMERIC(2, 1) NOT NULL CHECK (rating BETWEEN 0.5 AND 5.0),
    rated_at   TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (user_id, movie_id)
);

CREATE TABLE IF NOT EXISTS tags (
    user_id    INTEGER NOT NULL,
    movie_id   INTEGER NOT NULL REFERENCES movies (movie_id),
    tag        TEXT    NOT NULL,
    tagged_at  TIMESTAMPTZ NOT NULL
);
