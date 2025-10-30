import requests
import os
from dotenv import load_dotenv

# Load API credentials from .env file
load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")  # Basic plan has 1req/15min for recent and all tweets we need a pro plan"

def create_headers(bearer_token):
    """Return headers for authorization"""
    return {"Authorization": f"Bearer {bearer_token}"}

def get_tweets(query, start_time=None, end_time=None, max_results=10, next_token=None):
    """
    Fetch tweets using Twitter v2 Full Archive Search API
    """
    url = "https://api.twitter.com/2/tweets/search/recent"

    # Request parameters
    params = {
        "query": query,
        "tweet.fields": "id,text,author_id,created_at,lang,public_metrics",
        "expansions": "author_id",
        "user.fields": "username,name,location,verified,public_metrics",
        "max_results": max_results,  # 10–500
    }

    # Optional time filters
    if start_time:
        params["start_time"] = start_time  # ISO 8601 format: "2023-10-01T00:00:00Z"
    if end_time:
        params["end_time"] = end_time
    if next_token:
        params["next_token"] = next_token

    headers = create_headers(BEARER_TOKEN)
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")

    data = response.json()
    return data


if __name__ == "__main__":
    # Example usage
    query = "(Mukesh Ambani AI) lang:en -is:retweet"
    tweets = get_tweets(query, max_results=20)

    # Print fetched tweets
    for tweet in tweets.get("data", []):
        print(f"{tweet['created_at']} | @{tweet['author_id']} | {tweet['text']}\n")

    # Check for pagination
    meta = tweets.get("meta", {})
    if "next_token" in meta:
        print("More results available with next_token:", meta["next_token"])

