import asyncio
import os
import re
import io
import aiohttp
from lxml import html
from twikit import Client
from atproto_client.utils.text_builder import TextBuilder
from atproto import Client as BlueskyClient
from atproto import models

# --- CONFIGURATION ---
TWITTER_USER = os.getenv('TWITTER_USER', '')
BLUESKY_USER = os.getenv('BLUESKY_USER', '')
BLUESKY_PASS = os.getenv('BLUESKY_PASS', '')

# Pre-compile regex
SHORT_URL_PATTERN = re.compile(r'https://t.co/[a-zA-Z0-9]+')

# Initialize clients
client = Client('en-US')
bluesky_client = BlueskyClient()


async def get_metadata(session, url):
    """
    Extract OpenGraph metadata using lxml.
    Reads only first 10KB of HTML for efficiency.
    """
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                return None

            html_chunk = await response.content.read(1024 * 10)  # 10 KB only
            tree = html.fromstring(html_chunk)

            title = tree.findtext('.//title') or 'No title'
            description = (tree.xpath('//meta[@property="og:description"]/@content') or
                           tree.xpath('//meta[@name="description"]/@content') or
                           ['No description'])[0]
            thumbnail = (tree.xpath('//meta[@property="og:image"]/@content') or [None])[0]

            # Explicit cleanup
            del tree

            return {'title': title, 'description': description, 'thumbnail': thumbnail}
    except Exception as e:
        print(f"Metadata extraction warning: {e}")
        return None


async def fetch_image_to_memory(session, url, max_bytes=1024 * 1024):
    """
    Download image to RAM with optional max size (default 1MB).
    """
    try:
        async with session.get(url, timeout=15) as response:
            if response.status == 200:
                data = await response.content.read(max_bytes)
                return io.BytesIO(data)
    except Exception as e:
        print(f"Image download warning: {e}")
    return None


async def monitor_tweets(session, user_id):
    previous_tweet_id = None

    while True:
        try:
            tweets = await client.get_user_tweets(user_id, 'Tweets', count=1)

            if not tweets:
                print("No tweets returned.")
                await asyncio.sleep(60)
                continue

            latest_tweet = tweets[0]

            if previous_tweet_id == latest_tweet.id:
                print("No new tweets.")
            else:
                print(f"New Tweet: {latest_tweet.text[:50]}...")

                # Extract URLs
                full_url = latest_tweet.urls[0].get('expanded_url') if latest_tweet.urls else None
                embed = None

                # Process metadata & image
                if full_url:
                    print(f"Processing URL: {full_url}")
                    metadata = await get_metadata(session, full_url)

                    if metadata and metadata['thumbnail']:
                        img_buffer = await fetch_image_to_memory(session, metadata['thumbnail'])
                        if img_buffer:
                            thumb_blob = bluesky_client.upload_blob(img_buffer.getvalue())

                            embed = models.AppBskyEmbedExternal.Main(
                                external=models.AppBskyEmbedExternal.External(
                                    title=metadata['title'],
                                    description=metadata['description'],
                                    uri=full_url,
                                    thumb=thumb_blob.blob,
                                )
                            )

                            img_buffer.close()
                            del img_buffer
                            del thumb_blob

                    del metadata

                # Clean text
                clean_text = SHORT_URL_PATTERN.sub('', latest_tweet.text).strip()

                tb = TextBuilder()
                tb.text(clean_text)

                # Post to Bluesky
                try:
                    bluesky_client.send_post(tb, embed=embed)
                    print("Posted to Bluesky successfully.")
                    previous_tweet_id = latest_tweet.id
                except Exception as e:
                    print(f"Bluesky post error: {e}")


        except Exception as e:
            print(f"Critical Loop Error: {e}")

        await asyncio.sleep(60)


async def main():
    if not BLUESKY_USER or not BLUESKY_PASS:
        print("Set BLUESKY_USER and BLUESKY_PASS env vars.")
        return

    try:
        if os.path.exists('output_file.json'):
            client.load_cookies('output_file.json')
            print("Logged into Twitter (Cookies).")
        else:
            print("No Twitter cookies found.")

        bluesky_client.login(BLUESKY_USER, BLUESKY_PASS)
        print("Logged into Bluesky.")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    user = await client.get_user_by_screen_name(TWITTER_USER)
    if not user:
        print("Twitter user not found.")
        return

    print(f"Monitoring ID: {user.id}")

    async with aiohttp.ClientSession() as session:
        await monitor_tweets(session, user.id)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping bot...")
