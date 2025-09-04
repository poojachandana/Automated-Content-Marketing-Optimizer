import tweepy
import json


API_KEY = "BlU7y7PDr12BA3U0WkeBgZqDG"
API_SECRET_KEY = "ZisFXmjVtoJy0d0ZhY0ParjlwKPa0DPHYwzW4TectG1pWNX9kO"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAMmM3gEAAAAAMksCZE8n5VB5ldb6NBNUE5juLlU%3DQHa1lFdj11P01A0FfCYPTIRlDTtv0fiHMYZAr49dNbSVUgbTj7"
ACCESS_TOKEN = "1766159687911673856-eeZ9oo9i83qv51k5OEqiHLbXJvAvOq"
ACCESS_TOKEN_SECRET = "QpNGg1oX2s4ZGgmqLM3unP7pFmeIu0ISYHsXVFMDypVxD"

# Initialize client
twitterClient = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True,
)




# Get Bill Gates user info
user = twitterClient.get_user(username="BillGates")
user_id = user.data.id
print("🔹 Bill Gates User ID:", user_id)

# Get latest 5 tweets
tweets = twitterClient.get_users_tweets(
    user_id,
    max_results=50,
    tweet_fields=['created_at', 'public_metrics', 'text']
)

# Check if tweets exist
if tweets.data:
    # Convert to list of dictionaries
    tweets_list = [tweet.data for tweet in tweets.data]

    # Save tweets to JSON file
    file_name = "extracted_tweets.json"
    with open(file_name, "w") as json_file:
        json.dump(tweets_list, json_file, indent=4)






