import pandas as pd
import json
from run_prompt import execute_gemini

def top_5_selection(analysed_tweets, engagement_type: str):
    df = pd.DataFrame(analysed_tweets)
    filtered_df = df[df['engagement_type'] == engagement_type]
    return filtered_df.nlargest(5, columns=['engagement_score']).to_dict('records')

def create_tweet(analysed_tweets):
    prompt = (
        "write a tweet for newly releasing iphone 17 pro max with a18pro SoC launching with "
        "physically moving camera zoom, make this tweet more for camera enthusiast audience"
    )
    engagement_type = "like"
    top_5_tweets = top_5_selection(analysed_tweets, engagement_type)
    system_prompt = (
        f"Create an engaging twitter tweet for my tech company\n"
        f"PROMPT: {prompt}\n"
        "Here are some example tweets and their sentiment analysis with high user engagement of other similar companies\n"
        f"Example Tweets:\n{top_5_tweets}\n"
        "Create the tweet, compare it with the example tweets, and predict and explain why and how this tweet will perform well compared to the given examples."
    )

    out = execute_gemini(system_prompt)
    print("Raw Gemini output:", out)

    try:
        out_dict = json.loads(out)
        tweet = out_dict.get('tweet', 'No tweet generated')
        prediction = out_dict.get('prediction', 'No prediction provided')
        explanation = out_dict.get('explanation', 'No explanation provided')
    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        tweet = prediction = explanation = 'Error decoding response'
    except Exception as e:
        print("Unexpected error:", e)
        tweet = prediction = explanation = 'Error processing response'

    print("TWEET ======>", tweet)
    print("Prediction ======>", prediction)
    print("Explanation ======>", explanation)

if __name__ == "__main__":
    with open("analyzed_tweets.json") as f:
        data = json.load(f)
        parsed_tweets = [json.loads(t) if isinstance(t, str) else t for t in data]
        print("tweets loaded", parsed_tweets)
        create_tweet(parsed_tweets)
