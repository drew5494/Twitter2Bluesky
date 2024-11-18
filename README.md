# Twitter2Bluesky

Want to break free from billionaire-controlled X (formerly known as Twitter)? Still craving updates from accounts not yet on Bluesky? Well, do we have a project for you! This tool is designed to keep tabs on the latest tweets from a specific Twitter/X account in real-time and cross-post them to Bluesky, the decentralized social network. Using the twikit library, the script pulls the latest tweets from Twitter and seamlessly integrates with Bluesky's API for easy cross-posting.

Just a heads up—this script needs to keep running to do its thing. It checks for new tweets every 60 seconds, so if it stops, you'll miss out on those sweet updates!

## Install

UPDATE
Now using open-graph-scraper from Node JS 

To get started, install the required dependencies:
```bash
npm install open-graph-scraper
pip install asyncio aiohttp requests beautifulsoup4 twikit atproto
```
Use a browser extension to download cookies from your Twitter account. Save the cookies in a file named cookie.json and place it in the same directory as the scripts.

Run the cookie_generator.py script to create a login file compatible with Twikit.

Replace `target-twitter-screen-name` in the script with the desired Twitter username, and replace `your-bluesky-username` and `your-bluesky-password` with your Bluesky account credentials.

Run the twitter2bluesky.py script to fetch the latest tweets and post them!

## Checklist
- [X] Implement Twitter monitoring using twikit.
- [X] Integrate link expansion for shortened URLs.
- [X] Extract metadata for creating thumbnails (title, description, image) using BS4.
- [X] Authenticate and interact with the Bluesky API (atproto).
- [ ] Multiple account support.

