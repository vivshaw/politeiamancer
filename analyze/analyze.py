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
from pyspark.sql.functions import col, current_timestamp, from_json, from_unixtime, lower, udf
from pyspark.sql.types import FloatType, IntegerType, StringType, StructField, StructType  

# Cassandra and Kafka connection params
CASSANDRA_COMMENTS_TABLE = "r_politics_comments"
CASSANDRA_HOST = "cassandra"
CASSANDRA_KEYSPACE = "r_politics"
CASSANDRA_PORT = "9042"
KAFKA_BOOTSTRAP_SERVERS = "kafka1:9092"
KAFKA_TOPIC = "r_politics_comments"

# Schema of my Kafka data
kafka_schema = StructType([
    # ID
    StructField("fullname", StringType(), True),

    # Comment details
    StructField("author", StringType(), True),
    StructField("body", StringType(), True),
    StructField("downvotes", IntegerType(), True),
    StructField("permalink", StringType(), True),
    StructField("upvotes", IntegerType(), True),

    # Time
    StructField("timestamp", FloatType(), True),
])

@udf(returnType=FloatType())
def sentiment_score(text: str) -> float:
    """
    Spark UDF to calculate a sentiment score for a piece of text using VADER.
    (Can't be defined inside `RedditCommentAnalyzer` or else Spark complains, so it lives out here.)
    """
    sentiment_intensity_analyzer = SentimentIntensityAnalyzer()  
    valence_scores = sentiment_intensity_analyzer.polarity_scores(text)
    sentiment = valence_scores['compound']
    return sentiment

class RedditCommentAnalyzer:
    """
    A class that stands up a Spark instance and uses it to run streaming sentiment analysis
    on Reddit comment data. Data is pulled from Kafka and streamed into Cassandra.
    """
    def __init__(self) -> None:
        self.spark: SparkSession = SparkSession.builder \
            .appName("StreamProcessor") \
            .config('spark.cassandra.connection.host', CASSANDRA_HOST) \
            .config('spark.cassandra.connection.port', CASSANDRA_PORT) \
            .config('spark.cassandra.output.consistency.level','ONE') \
            .getOrCreate()

    def stream_comment_analysis(self) -> None:
        """
        Performs streaming data analysis on a live stream of /r/politics comments pulled from Kafka.

        Specifically:
         - calculates a sentiment score for each comment, using VADER
         - checks whether Biden or Trump is mentioned in each comment
        """
        # First, ingest the raw data from Kafka
        raw_df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
            .option("subscribe", KAFKA_TOPIC) \
            .load()
        
        # Parse out the JSON
        parsed_df = raw_df \
            .withColumn(
                "comment_json",
                from_json(col("value").cast("string"), kafka_schema) # Needs an explicit cast 'cause Spark infers type `BINARY`
            ) \
            .select(
                "comment_json.*"
            )

        # Munge the timestamps a bit.
        # We want a separate timestamp for the comment's timestamp, and the time we ran the analysis.
        with_timestamps_df = parsed_df \
            .withColumn("comment_timestamp", from_unixtime(col("timestamp"))) \
            .withColumn("analysis_timestamp", current_timestamp()) \
            .drop("timestamp")
        
        # Check whether Biden or Trump were mentioned
        with_mentions_df = with_timestamps_df \
            .withColumn("mentions_trump", lower(col("body")).like("%trump%")) \
            .withColumn("mentions_biden", lower(col("body")).like("%biden%"))
        
        # Calculate a sentiment score
        with_sentiments_df = with_mentions_df.withColumn('sentiment_score', sentiment_score(col("body")))

        # Write out to Cassandra
        with_sentiments_df \
            .writeStream \
            .format("org.apache.spark.sql.cassandra") \
            .option("checkpointLocation", "/tmp/checkpoint/") \
            .option("failOnDataLoss", "false") \
            .option("keyspace", CASSANDRA_KEYSPACE) \
            .option("table", CASSANDRA_COMMENTS_TABLE) \
            .start()
        
        self.spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    reddit_comment_analyzer = RedditCommentAnalyzer()
    reddit_comment_analyzer.stream_comment_analysis()