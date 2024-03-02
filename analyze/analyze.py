"""
Analyzes a live stream of Reddit comment data pulled from Kafka, using Spark, and stores
it in Cassandra for later visualization.

Sentiment scores are calculated using the VADER sentiment model:
Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment
Analysis of Social Media Text. Eighth International Conference on Weblogs and Social Media
(ICWSM-14). Ann Arbor, MI, June 2014.
"""

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    avg,
    col,
    current_timestamp,
    from_json,
    lit,
    lower,
    to_timestamp,
    udf,
    window,
)
from pyspark.sql.types import (
    FloatType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)
import uuid

# Cassandra and Kafka connection params
CASSANDRA_COMMENTS_TABLE = "r_politics_comments"
CASSANDRA_HOST = "cassandra"
CASSANDRA_KEYSPACE = "r_politics"
CASSANDRA_PORT = "9042"
KAFKA_BOOTSTRAP_SERVERS = "kafka1:9092"
KAFKA_TOPIC = "r_politics_comments"

# Schema of my Kafka data
kafka_schema = StructType(
    [
        # ID
        StructField("fullname", StringType(), True),
        # Comment details
        StructField("author", StringType(), True),
        StructField("body", StringType(), True),
        StructField("downvotes", IntegerType(), True),
        StructField("permalink", StringType(), True),
        StructField("upvotes", IntegerType(), True),
        # Time
        StructField("timestamp", IntegerType(), True),
    ]
)


@udf(returnType=FloatType())
def sentiment_score(text: str) -> float:
    """
    Spark UDF to calculate a sentiment score for a piece of text using VADER.
    (Can't be defined inside `RedditCommentAnalyzer` or else Spark complains, so it
    lives out here.)
    """
    sentiment_intensity_analyzer = SentimentIntensityAnalyzer()
    valence_scores = sentiment_intensity_analyzer.polarity_scores(text)
    sentiment = valence_scores["compound"]
    return sentiment


@udf(returnType=StringType())
def make_uuid():
    """
    Spark UDF to generate a UUID
    """
    return str(uuid.uuid1())


class RedditCommentAnalyzer:
    """
    A class that stands up a Spark instance and uses it to run streaming sentiment
    analysis on Reddit comment data. Data is pulled from Kafka and streamed into
    Cassandra.
    """

    def __init__(self) -> None:
        self.spark: SparkSession = (
            SparkSession.builder.appName("StreamProcessor")
            .config("spark.cassandra.connection.host", CASSANDRA_HOST)
            .config("spark.cassandra.connection.port", CASSANDRA_PORT)
            .config("spark.cassandra.output.consistency.level", "ONE")
            .getOrCreate()
        )

    def stream_comment_analysis(self) -> None:
        """
        Performs streaming data analysis on a live stream of /r/politics comments
        pulled from Kafka.

        Specifically:
         - calculates a sentiment score for each comment, using VADER
         - checks whether Biden or Trump is mentioned in each comment
        """
        # First, ingest the raw data from Kafka
        raw_df = (
            self.spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
            .option("subscribe", KAFKA_TOPIC)
            .load()
        )

        # Parse out the JSON
        parsed_df = raw_df.withColumn(
            "comment_json",
            from_json(
                col("value").cast("string"), kafka_schema
            ),  # Needs an explicit cast 'cause Spark infers type `BINARY`
        ).select("comment_json.*")

        # Munge the timestamps a bit.
        # We want a separate timestamp for the comment's timestamp, and the time we
        # ran the analysis.
        with_timestamps_df = (
            parsed_df.withColumn("comment_timestamp", to_timestamp(col("timestamp")))
            .withColumn("analysis_timestamp", current_timestamp())
            .drop("timestamp")
        )

        # Check whether Biden or Trump were mentioned
        with_mentions_df = with_timestamps_df.withColumn(
            "mentions_trump", lower(col("body")).like("%trump%")
        ).withColumn("mentions_biden", lower(col("body")).like("%biden%"))

        # Calculate a sentiment score
        with_sentiments_df = with_mentions_df.withColumn(
            "sentiment_score", sentiment_score(col("body"))
        )

        # Write out all comments to Cassandra
        with_sentiments_df.writeStream.format("org.apache.spark.sql.cassandra").option(
            "checkpointLocation", "/tmp/checkpoint/"
        ).option("failOnDataLoss", "false").option(
            "keyspace", CASSANDRA_KEYSPACE
        ).option("table", CASSANDRA_COMMENTS_TABLE).start()

        # Raw comments are not that useful, so let's do some aggregation!
        # Let's start with minute-by-minute average sentiment score.
        overall_moving_averages_df = (
            with_sentiments_df.withWatermark("comment_timestamp", "3 minutes")
            .groupBy(window("comment_timestamp", "3 minutes", "1 minute"))
            .agg(avg("sentiment_score").alias("sentiment_average"))
            .withColumn("uuid", make_uuid())
            .withColumn("type", lit("overall"))
            .withColumn("analysis_timestamp", col("window.end"))
            .drop("window")
        )

        # Write out batches of aggregated sentiment scores
        overall_moving_averages_df.writeStream.trigger(
            processingTime="10 seconds"
        ).foreachBatch(
            lambda df, _: df.write.format("org.apache.spark.sql.cassandra")
            .option("checkpointLocation", "/tmp/checkpoint/")
            .option("table", "sentiment_moving_average")
            .option("keyspace", CASSANDRA_KEYSPACE)
            .mode("append")
            .save()
        ).outputMode("update").start()

        # Now, average sentiment score for comments mentioning Trump.
        trump_moving_averages_df = (
            with_sentiments_df.filter(lower(col("body")).like("%trump%"))
            .withWatermark("comment_timestamp", "3 minutes")
            .groupBy(window("comment_timestamp", "3 minutes", "1 minute"))
            .agg(avg("sentiment_score").alias("sentiment_average"))
            .withColumn("uuid", make_uuid())
            .withColumn("type", lit("trump"))
            .withColumn("analysis_timestamp", col("window.end"))
            .drop("window")
        )

        # Write out batches of aggregated Trump sentiment scores
        trump_moving_averages_df.writeStream.trigger(
            processingTime="10 seconds"
        ).foreachBatch(
            lambda df, _: df.write.format("org.apache.spark.sql.cassandra")
            .option("checkpointLocation", "/tmp/checkpoint/")
            .option("table", "sentiment_moving_average")
            .option("keyspace", CASSANDRA_KEYSPACE)
            .mode("append")
            .save()
        ).outputMode("update").start()

        # Lastly, average sentiment score for comments mentioning Biden.
        biden_moving_averages_df = (
            with_sentiments_df.filter(lower(col("body")).like("%biden%"))
            .withWatermark("comment_timestamp", "3 minutes")
            .groupBy(window("comment_timestamp", "3 minutes", "1 minute"))
            .agg(avg("sentiment_score").alias("sentiment_average"))
            .withColumn("uuid", make_uuid())
            .withColumn("type", lit("biden"))
            .withColumn("analysis_timestamp", col("window.end"))
            .drop("window")
        )

        # Write out batches of aggregated Trump sentiment scores
        biden_moving_averages_df.writeStream.trigger(
            processingTime="10 seconds"
        ).foreachBatch(
            lambda df, _: df.write.format("org.apache.spark.sql.cassandra")
            .option("checkpointLocation", "/tmp/checkpoint/")
            .option("table", "sentiment_moving_average")
            .option("keyspace", CASSANDRA_KEYSPACE)
            .mode("append")
            .save()
        ).outputMode("update").start()

        self.spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    reddit_comment_analyzer = RedditCommentAnalyzer()
    reddit_comment_analyzer.stream_comment_analysis()
