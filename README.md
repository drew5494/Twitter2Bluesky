# Twitter2Bluesky

This project is designed to monitor the latest tweets from a specific Twitter account in real-time and post the updates to Bluesky, a decentralized social network. Using the `twikit` library, the script fetches the latest tweets from Twitter and will eventually integrate Bluesky's API for seamless cross-posting.

## Install
To get started, install the required dependencies:
```bash
pip install asyncio aiohttp requests beautifulsoup4 twikit atproto
```

## Checklist
- [ ] Implement Twitter monitoring using twikit.
- [ ] Integrate link expansion for shortened URLs.
- [ ] Extract metadata for creating thumbnails (title, description, image) using BS4.
- [ ] Authenticate and interact with the Bluesky API (atproto).
