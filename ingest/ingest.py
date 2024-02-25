"""Ingests comments from the /r/politics subreddit, and slaps 'em into Kafka."""

import asyncpraw
import asyncio
import os

from json import dumps
from kafka import KafkaProducer

# "I already am eating from the trash can all the time. The name of this trash can is ideology."
SUBREDDIT = "politics"
# I want to reference the app version in the `user_agent`
VERSION = os.getenv("VERSION")

class RedditCommentIngester:
    """
    A class that stands up a Reddit and Kafka client, and uses them to stream comment data.
    """
    def __init__(self) -> None:
        self.reddit = self.__initialize_reddit_client__()
        self.kafka_producer = KafkaProducer(
            api_version=(0, 10, 1),
            bootstrap_servers = ['kafka1:9092'],
            value_serializer = lambda x: dumps(x).encode('utf-8')
        )

    def __initialize_reddit_client__(self) -> None:
        """
        Set up the Reddit client instance.
        I'm using a read-only PRAW intance because I have no need to post comments.
        I picked `asyncpraw` because... ¯\_(ツ)_/¯

        Credentials need to be supplied via env var.
        """
        reddit = asyncpraw.Reddit(
            client_id = os.getenv("REDDIT_CLIENT_ID"),
            client_secret = os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent = f"python:vivshaw/politeiamancer:{VERSION} (by /u/vivshaw)",
        )

        return reddit

    async def stream(self) -> None:
        """
        The core application loop.
        All I do here is stream incoming comments, and attempt to dump them into Kafka.
        """
        subreddit = await self.reddit.subreddit(SUBREDDIT)

        async for comment in subreddit.stream.comments(skip_existing=False):
            try:
                # Turn the comment into somethin' JSON-serializable
                comment_as_json: dict[str, str] = {
                    # ID
                    "id": comment.id,
                    
                    # Comment details
                    "author": comment.author.name,
                    "body": comment.body,
                    "downvotes": comment.downs,
                    "name": comment.name,
                    "over_18": comment.over_18,
                    "permalink": comment.permalink,
                    "subreddit": comment.subreddit.display_name,
                    "timestamp": comment.created_utc,
                    "upvotes": comment.ups,
                }

                # Logs
                print(f"recv'd: {comment_as_json}")

                # Finally, send it to Kafka!
                self.kafka_producer.send("r_politics_comments", value=comment_as_json)

            except Exception as e:
                # If we failed to send to Kafka, let it fail and keep truckin'.
                print(f"Couldn't send comment to Kafka: {e}")

async def main():
    reddit_comment_ingester = RedditCommentIngester()
    foo = reddit_comment_ingester.stream()
    await foo

if __name__ == "__main__":
    asyncio.run(main())