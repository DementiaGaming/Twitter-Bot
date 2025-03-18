import tweepy
import os
from dotenv import load_dotenv
import requests
import praw
import random
import tkinter as tk
import customtkinter as ctk
import asyncio

load_dotenv()

#get api stuff
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")

#authenticate twitter api
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

#authenticate reddit api
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent="DramaBot/1.0 by u/YourRedditUsername"
)

#huggingface API details
API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct" # Mistral 7B model
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

#Add any subreddits you want to fetch posts from and feed into the ai here
subreddits = ["youtubedrama", "LivestreamFail", "insanepeopletwitter"]

def getRedditPosts(subreddits):
    global url
    subreddit_name = random.choice(subreddits)
    subreddit = reddit.subreddit(subreddit_name)

    top_posts = list(subreddit.hot(limit=20))

    if not top_posts:
        return "No trending posts found."

    post = random.choice(top_posts)
    title = post.title
    description = post.selftext
    url = post.url
    return f"📢 {title}\n{description}\n"

def tweetText(tweetText):
    client.create_tweet(text=tweetText)
    print(f"tweeted: {tweetText}")

def generateAiTextPrompt(prompt):
    response = requests.post(API_URL, headers=HEADERS, json={"inputs": prompt})
    response_json = response.json()
    
    if isinstance(response_json, list) and response_json:
        raw_text = response_json[0].get("generated_text", "Error: No response")
        
        cleaned_text = raw_text.split("\n")[-1].strip()
        return cleaned_text if cleaned_text else "Error: No response"
    
    return "Error: No response"


async def generateAndTweet():
    outputText.configure(text="Generating and tweeting...")
    try:
        #decides what the bot should tweet
        context = getRedditPosts(subreddits)
        print(context)
        text = generateAiTextPrompt(f"Here’s a messy Reddit post: '{context}'. Now, write a hilarious, unfiltered tweet reacting to it. Be sarcastic, dramatic, or ridiculous. No repeating, no hashtags, under 200 characters. also swear and use slang")
        print(f"Ai tweet: {text}")

        if text != "Error: No response":
            tweetText(f"{text}\n{url}")
        
        print("✅ Tweet posted!")
        outputText.configure(text="✅ Tweet posted!")

    except Exception as e:
        print(f"❌ Error: {e}")
        outputText.configure(text=f"❌ Error: {e}")

def check_async_loop():
    try:
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(0))
    except RuntimeError:
        pass
    root.after(100, check_async_loop)

root = ctk.CTk()
root.title("Twitter Bot")
root.geometry("800x400")

tweetButton = ctk.CTkButton(root, text="Generate and Tweet", command= lambda: asyncio.create_task(generateAndTweet()))
tweetButton.pack()

outputText = ctk.CTkLabel(root, text="")
outputText.pack()

root.mainloop()