CREATE KEYSPACE IF NOT EXISTS r_politics WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
USE r_politics;

CREATE TABLE IF NOT EXISTS r_politics_comments(
    -- ID
    fullname text,

    -- Comment details
    author text,
    body text,
    downvotes int,
    permalink text,
    upvotes int,

    -- Time
    analysis_timestamp timestamp,
    comment_timestamp timestamp,
    
    -- Analytics
    sentiment_score float,
    mentions_trump boolean,
    mentions_biden booolean,

    -- Keys
    PRIMARY KEY((author), comment_timestamp)
)
WITH CLUSTERING ORDER BY (comment_timestamp DESC);

CREATE TABLE IF NOT EXISTS r_politics_sentiment_moving_avg(
    -- ID
    id uuid,

    -- Time
    analysis_timestamp timestamp,

    -- Analytics
    overall_sentiment_score_avg float,
    biden_sentiment_score_avg float,
    trump_sentiment_Score_avg float,
    
    -- Keys
    PRIMARY KEY((id), analysis_timestamp))
WITH CLUSTERING ORDER BY (analysis_timestamp DESC);
