import os, tweepy
from datetime import datetime

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

def search_twitter_hazards(limit=10):
    client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)
    query="tsunami OR cyclone -is:retweet (lang:en OR lang:hi)"
    resp=client.search_recent_tweets(query=query,max_results=min(10,limit),
        tweet_fields=["created_at","lang","public_metrics"])
    tweets=[]
    for t in (resp.data or []):
        pm=t.public_metrics or {}
        tweets.append({
            "id":str(t.id),
            "created_at":getattr(t,"created_at",""),
            "lang":getattr(t,"lang",""),
            "text":t.text.replace("\n"," "),
            "likes":pm.get("like_count"),
            "retweets":pm.get("retweet_count"),
            "url":f"https://twitter.com/i/web/status/{t.id}"
        })
    return {"count":len(tweets),"items":tweets,"query":query}
