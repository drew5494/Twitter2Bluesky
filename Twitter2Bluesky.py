import asyncio
import os
import aiohttp
import re
import requests
from bs4 import BeautifulSoup
from twikit import Client
from atproto_client.utils.text_builder import TextBuilder
from atproto import Client as BlueskyClient
from atproto import models
from urllib.parse import urlparse

# Initialize Twikit and Bluesky clients
client = Client('en-US')
bluesky_client = BlueskyClient()

# Asynchronous image downloader
async def download_image_async(image_url, save_path):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(image_url) as response:
                if response.status == 200:
                    with open(save_path, 'wb') as file:
                        file.write(await response.read())
                    print(f"Image saved to {save_path}")
                else:
                    print(f"Failed to download image. Status code: {response.status}")
        except Exception as e:
            print(f"Error downloading image: {e}")

# Metadata extractor
def get_metadata(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the page: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string if soup.title else "No title found"
    description = soup.find("meta", {"name": "description"}) or soup.find("meta", {"property": "og:description"})
    description_content = description["content"] if description else "No description found"
    thumbnail = soup.find("meta", {"property": "og:image"})
    thumbnail_url = thumbnail["content"] if thumbnail and "content" in thumbnail.attrs else None
    
    return {
        "title": title,
        "description": description_content,
        "thumbnail": thumbnail_url
    }

# Expand shortened URLs
async def expand_url(short_url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(short_url, allow_redirects=False) as response:
                if response.status in [301, 302]:
                    return response.headers.get('Location', short_url)
                return short_url
        except Exception as e:
            print(f"Error expanding URL: {e}")
            return short_url

# Fetch latest tweets and post to Bluesky
async def fetch_latest_tweet(user_id):
    previous_tweet_id = None

    while True:
        try:
            tweets = await client.get_user_tweets(user_id, 'Tweets', count=1)
            if not tweets:
                print("No tweets found.")
                await asyncio.sleep(60)
                continue

            latest_tweet = tweets[0]
            tweet_id = latest_tweet.id
            tweet_text = latest_tweet.text

            if tweet_id == previous_tweet_id:
                print("No new tweets.")
            else:
                print(f"Latest Tweet: {tweet_text}")
                tb = TextBuilder()
                short_urls = re.findall(r'https://t.co/[a-zA-Z0-9]+', tweet_text)
                embed = None

                if short_urls:
                    for short_url in short_urls:
                        full_url = await expand_url(short_url)
                        print(f"Expanded link: {full_url}")
                        metadata = get_metadata(full_url)
                        tweet_text = re.sub(r'https://t.co/[a-zA-Z0-9]+', ' ', tweet_text)

                        if metadata:
                            title = metadata["title"]
                            description = metadata["description"]
                            thumbnail_url = metadata["thumbnail"]

                            if thumbnail_url and thumbnail_url.startswith("http"):
                                await download_image_async(thumbnail_url, "image.jpg")

                                if os.path.exists("image.jpg"):
                                    with open('image.jpg', 'rb') as f:
                                        img_data = f.read()
                                    thumb = bluesky_client.upload_blob(img_data)
                                    embed = models.AppBskyEmbedExternal.Main(
                                        external=models.AppBskyEmbedExternal.External(
                                            title=title,
                                            description=description,
                                            uri=full_url,
                                            thumb=thumb.blob,
                                        )
                                    )
                                os.remove("image.jpg")
                        
                tb.text(tweet_text.strip())

                try:
                    bluesky_post = bluesky_client.send_post(tb, embed=embed)
                    print(f"Posted to Bluesky: {bluesky_post}")
                except Exception as e:
                    print(f"Error posting to Bluesky: {e}")

                previous_tweet_id = tweet_id
        except Exception as e:
            print(f"Error fetching tweet: {e}")
        
        print("Sleeping...")
        await asyncio.sleep(60)

# Main function
async def main():
    try:
        client.load_cookies('output_file.json')  # Replace with actual cookie file path
        print("Logged into Twitter.")
    except Exception as e:
        print(f"Failed to log in to Twitter: {e}")
        return
    
    try:
        bluesky_client.login('your-bluesky-username', 'your-bluesky-password')  # Replace with Bluesky credentials
        print("Logged into Bluesky.")
    except Exception as e:
        print(f"Error logging into Bluesky: {e}")
        return

    screen_name = 'target-twitter-screen-name'  # Replace with target Twitter screen name
    user = await client.get_user_by_screen_name(screen_name)
    if user:
        print(f"Found Twitter ID: {user.id}")
        await fetch_latest_tweet(user.id)
    else:
        print("User not found.")

# Run the main function
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Script terminated by user.")