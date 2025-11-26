import asyncio
import os
import re
import io
import aiohttp
from bs4 import BeautifulSoup
from twikit import Client
from atproto_client.utils.text_builder import TextBuilder
from atproto import Client as BlueskyClient
from atproto import models
import gc # Added for optional manual cleanup/debugging

# --- CONFIGURATION ---
# Load from Environment variables for better memory hygiene in containers
# Or fallback to hardcoded strings if running locally
TWITTER_USER = os.getenv('TWITTER_USER', '')
BLUESKY_USER = os.getenv('BLUESKY_USER', '')
BLUESKY_PASS = os.getenv('BLUESKY_PASS', '')

# Pre-compile regex to save CPU/Memory in loop
SHORT_URL_PATTERN = re.compile(r'https://t.co/[a-zA-Z0-9]+')

# Initialize Clients
client = Client('en-US')
bluesky_client = BlueskyClient()

async def get_metadata(session, url):
    """
    Extracts OpenGraph metadata using the shared async session.
    Optimized: Only reads the first 10KB of HTML and uses the efficient 'lxml' parser.
    """
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                return None
            
            # --- OPTIMIZATION 2: Read only the first 10KB of the response ---
            # This is sufficient to capture title and meta tags, reducing the memory required 
            # for parsing large articles/pages.
            html_chunk = await response.content.read(1024 * 10) 
            
            # --- OPTIMIZATION 1: Use lxml parser ---
            # You must ensure 'pip install lxml' has been run.
            soup = BeautifulSoup(html_chunk, 'lxml')
            
            # Efficient extraction using simple lookups
            title = soup.title.string if soup.title else "No title"
            
            # Try OG tags first, fall back to standard meta
            og_desc = soup.find("meta", property="og:description")
            std_desc = soup.find("meta", attrs={"name": "description"})
            description = (og_desc or std_desc or {}).get("content", "No description")
            
            og_img = soup.find("meta", property="og:image")
            thumbnail = og_img["content"] if og_img else None
            
            # Explicitly delete the soup object to help Python's GC
            del soup 
            
            return {
                "title": title,
                "description": description,
                "thumbnail": thumbnail
            }
    except Exception as e:
        print(f"Metadata extraction warning: {e}")
        return None

async def fetch_image_to_memory(session, url):
    """
    Downloads image directly to RAM (BytesIO) to avoid Disk I/O overhead.
    """
    try:
        async with session.get(url, timeout=15) as response:
            if response.status == 200:
                data = await response.read()
                return io.BytesIO(data) # Return in-memory binary stream
    except Exception as e:
        print(f"Image download warning: {e}")
    return None

async def main():
    # 1. Login Logic
    if not BLUESKY_USER or not BLUESKY_PASS:
        print("Set BLUESKY_USER and BLUESKY_PASS env vars or edit config.")
        return

    try:
        # Check if cookies exist before loading
        if os.path.exists('output_file.json'):
            client.load_cookies('output_file.json')
            print("Logged into Twitter (Cookies).")
        else:
            print("No Twitter cookies found. Please ensure output_file.json exists.")
            # Optional: Add manual login logic here if needed
            
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

    # 2. Shared Session & Loop
    # Create ONE session for the entire lifecycle
    async with aiohttp.ClientSession() as session:
        await monitor_tweets(session, user.id)

async def monitor_tweets(session, user_id):
    previous_tweet_id = None
    
    while True:
        try:
            # Twikit fetch
            tweets = await client.get_user_tweets(user_id, 'Tweets', count=1)
            
            if not tweets:
                print("No tweets returned.")
                await asyncio.sleep(60)
                continue

            latest_tweet = tweets[0]
            
            if previous_tweet_id == latest_tweet.id:
                print("No new tweets.")
            else:
                # --- NEW TWEET PROCESSING ---
                print(f"New Tweet: {latest_tweet.text[:50]}...")
                
                # Extract URLs
                full_url = None
                if latest_tweet.urls:
                    full_url = latest_tweet.urls[0].get('expanded_url')
                
                embed = None
                
                # Process Embeds (Metadata & Images)
                if full_url:
                    print(f"Processing URL: {full_url}")
                    metadata = await get_metadata(session, full_url)
                    
                    if metadata and metadata['thumbnail']:
                        # Download directly to memory buffer
                        img_buffer = await fetch_image_to_memory(session, metadata['thumbnail'])
                        
                        if img_buffer:
                            # Upload blob directly from RAM
                            thumb_blob = bluesky_client.upload_blob(img_buffer.getvalue())
                            
                            embed = models.AppBskyEmbedExternal.Main(
                                external=models.AppBskyEmbedExternal.External(
                                    title=metadata['title'],
                                    description=metadata['description'],
                                    uri=full_url,
                                    thumb=thumb_blob.blob,
                                )
                            )
                            # Explicit cleanup to minimize memory spikes
                            img_buffer.close()
                            del img_buffer
                            del thumb_blob
                            
                    del metadata # Clean up metadata dict

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
                
                # --- OPTIONAL: Force Garbage Collection ---
                # Helps ensure memory from the last processing run is released internally.
                gc.collect() 

        except Exception as e:
            print(f"Critical Loop Error: {e}")

        # Smart sleep
        await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping bot...")