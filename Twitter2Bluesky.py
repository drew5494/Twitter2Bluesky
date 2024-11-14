import asyncio
from twikit import Client

client = Client('en-US')

async def fetch_latest_tweet(user_id):
    previous_tweet_id = None  # Variable to store the previous tweet's ID
    
    while True:
        # Retrieve the latest tweet (the first tweet in the response)
        tweets = await client.get_user_tweets(user_id, 'Tweets', count=1)
        
        if tweets:
            latest_tweet = tweets[0]  # The first tweet is the latest one
            tweet_id = latest_tweet.id
            tweet_text = latest_tweet.text

            # Check if the tweet is a duplicate
            if tweet_id == previous_tweet_id:
                print("No new tweets, duplicate detected.")
            else:
                print(f"Latest Tweet ID: {tweet_id}")
                print(f"Latest Tweet Text: {tweet_text}")
                previous_tweet_id = tweet_id  # Update the previous tweet ID to the current one
        else:
            print("No tweets found.")
        
        # Sleep for 60 seconds before fetching the next tweet
        await asyncio.sleep(60)

async def main():
    await client.login(
        auth_info_1='YPUR_USERNAME',
        auth_info_2='YOUR_EMAIL',
        password='YOUR_PASSWORD'
    )
    
    # Search for the user
    result = await client.search_user('ACCOUNT_NAME')
    
    # Look for a user with screen_name matching 
    for user in result:
        if user.screen_name.lower() == 'ACCOUNT_NAME':  # Match screen_name exactly
            user_id = user.id
            print(f"Found user ID for account: {user_id}")
            break
    else:
        print("user not found.")
        return

    # Start continuously fetching the latest tweet
    await fetch_latest_tweet(user_id)

# Run the main function to start the process
asyncio.run(main())
