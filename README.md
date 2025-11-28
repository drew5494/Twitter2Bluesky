# TwitterMirrorBot

Want to break free from billionaire-controlled X (formerly Twitter) but still want updates from accounts not yet on Bluesky? **TwitterMirrorBot** has you covered!

This tool monitors a specific Twitter/X account in real-time and cross-posts new tweets to **Bluesky**, the decentralized social network. Powered by the **twikit** library, it fetches the latest tweets and seamlessly posts them via the Bluesky API.

> ⚠️ Note: This script must keep running to work. It checks for new tweets every 60 seconds, so if it stops, updates will be missed.

---

## Features
- ✅ Monitor Twitter/X accounts in real-time using **twikit**
- ✅ Expand shortened URLs automatically
- ✅ Extract metadata (title, description, image) for thumbnails using **BeautifulSoup**
- ✅ Authenticate and post to **Bluesky** via **atproto**
- ✅ Support multiple accounts
- ⬜ Support for replies and media (coming soon)

---

## Installation

Install the required Python dependencies:

```bash
pip install aiohttp twikit atproto 
```

---

## Setup

1. Use a browser extension to export cookies from your Twitter account.
2. Save the cookies as `cookie.json` in the same directory as the scripts.
3. Run `cookie_generator.py` to generate a login file.
4. Set environment variables for:
   - Your Twitter account to monitor
   - Your Bluesky account to post to
5. Run `twitter2bluesky.py` and keep it running.

---

## Usage

Once running, the bot will check for new tweets every minute and automatically cross-post them to Bluesky.
