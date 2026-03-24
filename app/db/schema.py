import duckdb


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS vk_users (
    user_id BIGINT PRIMARY KEY,
    vk_user_id BIGINT UNIQUE,
    display_name VARCHAR,
    profile_url VARCHAR
);
CREATE SEQUENCE IF NOT EXISTS seq_vk_users START 1;

CREATE TABLE IF NOT EXISTS vk_posts (
    post_id BIGINT PRIMARY KEY,
    vk_post_id VARCHAR UNIQUE,
    author_id BIGINT,
    published_at TIMESTAMP,
    text TEXT,
    like_count INTEGER,
    comment_count INTEGER,
    FOREIGN KEY(author_id) REFERENCES vk_users(user_id)
);
CREATE SEQUENCE IF NOT EXISTS seq_vk_posts START 1;

CREATE TABLE IF NOT EXISTS vk_comments (
    comment_id BIGINT PRIMARY KEY,
    vk_comment_id VARCHAR UNIQUE,
    post_id BIGINT,
    author_id BIGINT,
    published_at TIMESTAMP,
    text TEXT,
    like_count INTEGER,
    FOREIGN KEY(post_id) REFERENCES vk_posts(post_id),
    FOREIGN KEY(author_id) REFERENCES vk_users(user_id)
);
CREATE SEQUENCE IF NOT EXISTS seq_vk_comments START 1;

CREATE TABLE IF NOT EXISTS nlp_analysis_posts (
    post_an_id BIGINT PRIMARY KEY,
    post_id BIGINT UNIQUE,
    user_post_id BIGINT,
    n_words INTEGER,
    n_inform_word INTEGER,
    sentiment VARCHAR,
    sentiment_score DOUBLE,
    toxicity_score DOUBLE,
    topics TEXT,
    top VARCHAR,
    FOREIGN KEY(post_id) REFERENCES vk_posts(post_id),
    FOREIGN KEY(user_post_id) REFERENCES vk_users(user_id)
);
CREATE SEQUENCE IF NOT EXISTS seq_nlp_analysis_posts START 1;

CREATE TABLE IF NOT EXISTS nlp_analysis_comments (
    com_an_id BIGINT PRIMARY KEY,
    post_id BIGINT,
    comment_id BIGINT UNIQUE,
    n_words INTEGER,
    n_inform_word INTEGER,
    sentiment VARCHAR,
    sentiment_score DOUBLE,
    toxicity_score DOUBLE,
    topics TEXT,
    FOREIGN KEY(post_id) REFERENCES vk_posts(post_id),
    FOREIGN KEY(comment_id) REFERENCES vk_comments(comment_id)
);
CREATE SEQUENCE IF NOT EXISTS seq_nlp_analysis_comments START 1;

CREATE INDEX IF NOT EXISTS idx_vk_users_vk_user_id ON vk_users(vk_user_id);
CREATE INDEX IF NOT EXISTS idx_vk_posts_author_id ON vk_posts(author_id);
CREATE INDEX IF NOT EXISTS idx_vk_posts_published_at ON vk_posts(published_at);
CREATE INDEX IF NOT EXISTS idx_vk_comments_post_id ON vk_comments(post_id);
CREATE INDEX IF NOT EXISTS idx_vk_comments_author_id ON vk_comments(author_id);
CREATE INDEX IF NOT EXISTS idx_nlp_posts_post_id ON nlp_analysis_posts(post_id);
CREATE INDEX IF NOT EXISTS idx_nlp_comments_comment_id ON nlp_analysis_comments(comment_id);

CREATE OR REPLACE MACRO fn_engagement_score(likes, comments) AS (
    COALESCE(likes, 0) + COALESCE(comments, 0) * 2
);

CREATE OR REPLACE MACRO fn_sentiment_bucket(score) AS (
    CASE
        WHEN score > 0.03 THEN 'positive'
        WHEN score < -0.03 THEN 'negative'
        ELSE 'neutral'
    END
);

CREATE OR REPLACE MACRO get_posts_by_period(date_from, date_to, min_likes := 0) AS TABLE (
    SELECT
        p.post_id,
        p.vk_post_id,
        u.display_name AS author_name,
        p.published_at,
        p.text,
        p.like_count,
        p.comment_count,
        fn_engagement_score(p.like_count, p.comment_count) AS engagement_score,
        a.sentiment,
        a.sentiment_score,
        a.toxicity_score
    FROM vk_posts p
    LEFT JOIN vk_users u ON u.user_id = p.author_id
    LEFT JOIN nlp_analysis_posts a ON a.post_id = p.post_id
    WHERE p.published_at BETWEEN date_from AND date_to
      AND COALESCE(p.like_count, 0) >= min_likes
    ORDER BY engagement_score DESC, p.published_at DESC
);
"""


def init_schema(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(SCHEMA_SQL)
