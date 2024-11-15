# Twitter2Bluesky

This project is designed to monitor the latest tweets from a specific Twitter / X account in real-time and post the updates to Bluesky, a decentralized social network. Using the `twikit` library, the script fetches the latest tweets from Twitter and integrates Bluesky's API for seamless cross-posting.

To function properly, the script must be kept running continuously. It checks for new tweets every 60 seconds. If the script stops running, it will no longer monitor or post updates.

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

