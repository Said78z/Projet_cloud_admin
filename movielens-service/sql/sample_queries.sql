-- Sample queries for the MovieLens service
-- Useful for manual testing and query-plan inspection.

-- 1. Search movies by partial title (case-insensitive)
SELECT movie_id, title, genres
FROM movies
WHERE LOWER(title) LIKE LOWER('%matrix%')
ORDER BY title;

-- 2. Filter movies by genre
SELECT movie_id, title, genres
FROM movies
WHERE genres ILIKE '%Action%'
ORDER BY title
LIMIT 20;

-- 3. Movie detail with rating statistics
SELECT
    m.movie_id,
    m.title,
    m.genres,
    ROUND(AVG(r.rating)::numeric, 2) AS avg_rating,
    COUNT(r.rating)                  AS num_ratings
FROM movies m
LEFT JOIN ratings r ON r.movie_id = m.movie_id
WHERE m.movie_id = 1
GROUP BY m.movie_id, m.title, m.genres;

-- 4. Top 10 movies with at least 50 ratings
SELECT
    m.movie_id,
    m.title,
    m.genres,
    ROUND(AVG(r.rating)::numeric, 2) AS avg_rating,
    COUNT(r.rating)                  AS num_ratings
FROM movies m
JOIN ratings r ON r.movie_id = m.movie_id
GROUP BY m.movie_id, m.title, m.genres
HAVING COUNT(r.rating) >= 50
ORDER BY avg_rating DESC, num_ratings DESC
LIMIT 10;

-- 5. Per-genre statistics (count of movies + average rating)
SELECT
    genre,
    COUNT(DISTINCT m.movie_id)       AS num_movies,
    ROUND(AVG(r.rating)::numeric, 2) AS avg_rating
FROM movies m,
     regexp_split_to_table(m.genres, '\|') AS genre
LEFT JOIN ratings r ON r.movie_id = m.movie_id
GROUP BY genre
ORDER BY num_movies DESC;

-- 6. Global rating-value distribution
SELECT rating, COUNT(*) AS cnt
FROM ratings
GROUP BY rating
ORDER BY rating;
