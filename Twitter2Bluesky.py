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
from urllib.parse import urlparse, urlunparse
import subprocess
import json
import aiofiles
import certifi

# Initialize Twikit and Bluesky clients
client = Client('en-US')
bluesky_client = BlueskyClient()

# Main function
async def main():
    print("Select an option:")
    print("1. BeautifulSoup (BS4) for metadata extraction")
    print("2. Open Graph Scraper (Node.js) for metadata extraction")
    choice = input("Enter 1 or 2: ").strip()

    if choice not in ["1", "2"]:
        print("Invalid choice. Exiting...")
        return

    twitter_screen_name = input("Enter the Twitter screen name (or leave blank to use default): ").strip() or "cp24"
    bluesky_username = input("Enter your Bluesky username: ").strip()
    bluesky_password = input("Enter your Bluesky password: ").strip()

    if not bluesky_username or not bluesky_password:
        print("Bluesky username and password are required.")
        return

    try:
        client.load_cookies('output_file.json')
        print("Logged into Twitter.")
    except Exception as e:
        print(f"Failed to log in to Twitter: {e}")
        return

    try:
        bluesky_client.login(bluesky_username, bluesky_password)
        print("Logged into Bluesky.")
    except Exception as e:
        print(f"Error logging into Bluesky: {e}")
        return

    user = await client.get_user_by_screen_name(twitter_screen_name)
    if user:
        print(f"Found Twitter ID: {user.id}")
        await fetch_latest_tweet(user.id, choice)
    else:
        print("User not found.")

# Fetch latest tweets and post to Bluesky
async def fetch_latest_tweet(user_id, choice):
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
                # general_url_pattern = r'https?://[^\s]+'
                short_urls = re.findall(r'https://t.co/[a-zA-Z0-9]+', tweet_text)
                print(f"Short : {short_urls}")
                embed = None
                title, description, thumbnail_url = None, None, None

                if short_urls:
                    for url_info in latest_tweet.urls:
                        expanded_url = url_info.get('expanded_url')  # Get the 'expanded_url' value
                        full_url = expanded_url
                        print("Expanded URL:", expanded_url)
                    if choice == "1":
                        metadata = get_metadata(full_url)
                        title = metadata["title"]
                        description = metadata["description"]
                        thumbnail_url = metadata["thumbnail"]
                    elif choice == "2":
                        try:
                            print("FULL", full_url)
                            result = subprocess.run(['node', 'index.js', full_url], capture_output=True, text=True)
                            if result.returncode == 0:
                                print("JS:", result.stdout)
                            else:
                                print("Error executing JavaScript:", result.stderr)
                        except Exception as e:
                            print(f"Error running JavaScript script: {e}")
                        with open('open_graph_data.json', 'r', encoding='utf-8') as file:
                            data = json.load(file)
                        title = data["result"].get("ogTitle", "No title found")
                        description = data["result"].get("ogDescription", "No description found")
                        thumbnail_url = data["result"].get("ogImage", [{"url": None}])[0]["url"]
                        os.remove('open_graph_data.json')

                tweet_text = re.sub(r'https://t.co/[a-zA-Z0-9]+', ' ', tweet_text)
                # print("thumb", thumbnail_url)
                if thumbnail_url and thumbnail_url.startswith("http"):
                    print("RD img")
                    success = await download_image_async(thumbnail_url, "image.jpg")
                    if success:
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

# Get metadata using BeautifulSoup (BS4)
def get_metadata(url):
    try:
        response = requests.get(url, verify=certifi.where())
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the page: {e}")
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string if soup.title else "No title found"
    description = soup.find("meta", {"name": "description"}) or soup.find("meta", {"property": "og:description"})
    description_content = description["content"] if description else "No description found"
    thumbnail = soup.find("meta", {"property": "og:image"})
    thumbnail_url = thumbnail["content"] if thumbnail and "content" in thumbnail.attrs else None
    
    return {"title": title, "description": description_content, "thumbnail": thumbnail_url}

# Download image asynchronously
async def download_image_async(url, filename):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    async with aiofiles.open(filename, mode='wb') as f:
                        await f.write(await response.read())
                    print(f"Image downloaded successfully: {filename}")
                    return True
                else:
                    print(f"Failed to download image. HTTP Status: {response.status}")
                    return False
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False

# Start the program
if __name__ == "__main__":
    asyncio.run(main())
