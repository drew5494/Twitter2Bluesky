# Twitter2Bluesky

Want to break free from billionaire-controlled X (formerly known as Twitter)? Still craving updates from accounts not yet on Bluesky? Well, do we have a project for you! This tool is designed to keep tabs on the latest tweets from a specific Twitter/X account in real-time and cross-post them to Bluesky, the decentralized social network. Using the twikit library, the script pulls the latest tweets from Twitter and seamlessly integrates with Bluesky's API for easy cross-posting.

Just a heads up—this script needs to keep running to do its thing. It checks for new tweets every 60 seconds, so if it stops, you'll miss out on those sweet updates!

## Install
To get started, install the required dependencies:
```bash
pip install asyncio aiohttp requests beautifulsoup4 git+https://github.com/mdmrcglu/twikit.git
 atproto
```
Use a browser extension to download cookies from your Twitter account, then utilize the cookie_generator tool to create a login file compatible with twikit.

## Checklist
- [X] Implement Twitter monitoring using twikit.
- [X] Integrate link expansion for shortened URLs.
- [X] Extract metadata for creating thumbnails (title, description, image) using BS4.
- [X] Authenticate and interact with the Bluesky API (atproto).
- [ ] Multiple account support.

