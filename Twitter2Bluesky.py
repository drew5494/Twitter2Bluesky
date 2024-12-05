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

# Initialize Twikit and Bluesky clients
client = Client('en-US')
bluesky_client = BlueskyClient()

# Asynchronous image downloader
async def download_image_async(image_url, save_path):
    print(f"Starting download for {image_url}")
    timeout = aiohttp.ClientTimeout(total=10)  # 10-second timeout
    headers = {'User-Agent': 'Mozilla/5.0'}  # Mimic a browser

    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            print("Making request...")
            async with session.get(image_url, headers=headers) as response:
                print(f"Response received: {response.status}")
                if response.status == 200:
                    async with aiofiles.open(save_path, 'wb') as file:
                        await file.write(await response.read())
                    print(f"Image saved to {save_path}")
                else:
                    print(f"Failed to download image. Status code: {response.status}")
        except Exception as e:
            print(f"Error: {e}")

# Metadata extractor
# def get_metadata(url):
#     try:
#         response = requests.get(url, timeout=10)
#         response.raise_for_status()
#     except requests.exceptions.RequestException as e:
#         print(f"Failed to retrieve the page: {e}")
#         return None
    
#     soup = BeautifulSoup(response.text, 'html.parser')
#     title = soup.title.string if soup.title else "No title found"
#     description = soup.find("meta", {"name": "description"}) or soup.find("meta", {"property": "og:description"})
#     description_content = description["content"] if description else "No description found"
#     thumbnail = soup.find("meta", {"property": "og:image"})
#     thumbnail_url = thumbnail["content"] if thumbnail and "content" in thumbnail.attrs else None
    
#     return {
#         "title": title,
#         "description": description_content,
#         "thumbnail": thumbnail_url
#     }


# Function to clean up the URL by removing unwanted query parameters
def clean_url(url):
    parsed_url = urlparse(url)
    
    # Remove query parameters (you can add more conditions if needed)
    cleaned_url = urlunparse(parsed_url._replace(query=""))
    
    return cleaned_url

# Expand shortened URLs and clean them
async def expand_url(short_url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(short_url, allow_redirects=False) as response:
                if response.status in [301, 302]:
                    full_url = response.headers.get('Location', short_url)
                else:
                    full_url = short_url
                
                # Clean the URL by removing query parameters
                cleaned_url = clean_url(full_url)
                return cleaned_url
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
                general_url_pattern = r'https?://[^\s]+'
                short_urls = re.findall(r'https://t.co/[a-zA-Z0-9]+', tweet_text)
                embed = None

                if short_urls:
                    full_url = await expand_url(short_urls[0])
                    print(f"Expanded link: {full_url}")
                    # metadata = get_metadata(full_url)
                else:
                    # If no short URLs, check for general URLs
                    general_urls = re.findall(general_url_pattern, tweet_text)
                    if general_urls:
                        full_url = general_urls
                        print("Found general URLs:", general_urls)
                    else:
                        print("No URLs found.")

                try:
                # Pass the URL as an argument to the Node.js script
                    result = subprocess.run(['node', 'index.js', full_url], capture_output=True, text=True)

                    # Check if the script executed successfully
                    if result.returncode == 0:
                        print("JS:", result.stdout)
                    else:
                        print("Error executing JavaScript:", result.stderr)
                except Exception as e:
                    print(f"Error running JavaScript script: {e}")

                # Open and load JSON from a file
                with open('open_graph_data.json', 'r', encoding='utf-8') as file:
                    data = json.load(file)

                # Extract fields
                title = data["result"].get("ogTitle", "No title found")
                description = data["result"].get("ogDescription", "No description found")
                thumbnail_url = data["result"].get("ogImage", [{"url": None}])[0]["url"]

                os.remove('open_graph_data.json')

                # Print the extracted fields
                # print("ogTitle:", title)
                # print("ogDescription:", description)
                # print("ogImage:", thumbnail_url)
                
                # title = metadata["title"]
                # description = metadata["description"]
                # thumbnail_url = metadata["thumbnail"]

                tweet_text = re.sub(r'https://t.co/[a-zA-Z0-9]+', ' ', tweet_text)

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
        bluesky_client.login('account.bsky.social', 'your-bluesky-password')  # Replace with Bluesky credentials
        print("Logged into Bluesky.")
    except Exception as e:
        print(f"Error logging into Bluesky: {e}")
        return

    screen_name = 'abc'  # Replace with target Twitter screen name
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
