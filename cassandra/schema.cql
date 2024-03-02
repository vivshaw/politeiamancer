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
    mentions_biden boolean,

    -- Keys
    PRIMARY KEY((fullname), comment_timestamp)
)
WITH CLUSTERING ORDER BY (comment_timestamp DESC);

CREATE TABLE IF NOT EXISTS sentiment_moving_average(
    -- ID
    uuid uuid,

    --Time
    analysis_timestamp timestamp,

    -- Analytics
    sentiment_average float,
    type text,

    -- Keys
    PRIMARY KEY((type), analysis_timestamp))
WITH CLUSTERING ORDER BY (analysis_timestamp DESC);
CREATE INDEX IF NOT EXISTS ON sentiment_moving_average (uuid);