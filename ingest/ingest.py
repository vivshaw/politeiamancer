import asyncpraw
import asyncio
import os

VERSION = os.getenv("VERSION")

class RedditCommentIngester:
    def __init__(self) -> None:
        self.reddit = self.__initialize_reddit_client__()

    def __initialize_reddit_client__(self) -> None:
        reddit = asyncpraw.Reddit(
            client_id = os.getenv("REDDIT_CLIENT_ID"),
            client_secret = os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent = f"python:vivshaw/politeiamancer:{VERSION} (by /u/vivshaw)",
        )

        return reddit

    async def stream(self) -> None:
        subreddit = await self.reddit.subreddit("politics")
        async for comment in subreddit.stream.comments(skip_existing=False):
            print(comment.body)

async def main():
    reddit_comment_ingester = RedditCommentIngester()
    foo = reddit_comment_ingester.stream()
    await foo

if __name__ == "__main__":
    asyncio.run(main())