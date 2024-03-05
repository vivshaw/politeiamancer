CREATE KEYSPACE IF NOT EXISTS r_politics WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
USE r_politics;

CREATE TABLE IF NOT EXISTS sentiment_moving_average(
    -- ID
    uuid uuid,

    --Time
    window_timestamp timestamp,

    -- Analytics
    sentiment_average float,
    type text,

    -- Keys
    PRIMARY KEY((type), window_timestamp))
WITH CLUSTERING ORDER BY (window_timestamp DESC);
CREATE INDEX IF NOT EXISTS ON sentiment_moving_average (uuid);