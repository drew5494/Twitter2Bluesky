# TwitterMirrorBot

Want to break free from billionaire-controlled X (formerly known as Twitter)? Still craving updates from accounts not yet on Bluesky? Well, do we have a project for you! This tool is designed to keep tabs on the latest tweets from a specific Twitter/X account in real-time and cross-post them to Bluesky, the decentralized social network. Using the twikit library, the script pulls the latest tweets from Twitter and seamlessly integrates with Bluesky's API for easy cross-posting.

Just a heads up—this script needs to keep running to do its thing. It checks for new tweets every 60 seconds, so if it stops, you'll miss out on those sweet updates!

## Install

To get started, install the required dependencies:
```bash
pip install aiohttp beautifulsoup4 twikit atproto
```
Use a browser extension to download cookies from your Twitter account. Save the cookies in a file named cookie.json and place it in the same directory as the scripts.

Run the cookie_generator.py script to generate a login file.

Run the twitter2bluesky.py script and follow the command-line instructions.

You may use either BeautifulSoup or Open Graph Scraper (Node.js)

## Checklist
- [X] Implement Twitter monitoring using twikit.
- [X] Integrate link expansion for shortened URLs.
- [X] Extract metadata for creating thumbnails (title, description, image) using BS4.
- [X] Authenticate and interact with the Bluesky API (atproto).
- [ ] Multiple account support.

## Support Me
[![Support Me](https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimg.buymeacoffee.com%2Fapi%2F%3Furl%3DaHR0cHM6Ly9jZG4uYnV5bWVhY29mZmVlLmNvbS91cGxvYWRzL3Byb2plY3RfdXBkYXRlcy8yMDIxLzA1LzkxOGJjMGZmYWU5YTE4NjU1NTNkNTRiYzExZTY1YzRiLmdpZg%3D%3D%26height%3D600%26width%3D1200&f=1&nofb=1&ipt=5a6439673445b7c068bb3874ad7e660256a3f879c70e04a0d60d574e628f6869&ipo=images)](https://github.com/sponsors/drew5494?frequency=recurring)
