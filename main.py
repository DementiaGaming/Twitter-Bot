import tweepy
import os
from dotenv import load_dotenv
import requests
import praw
import random
import tkinter as tk
import customtkinter as ctk
import subprocess

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

context = ""
tweetText = ""
prompt = "Now, write a hilarious, unfiltered tweet reacting to the reddit post. Be sarcastic, dramatic, or ridiculous. No repeating, no hashtags, under 200 characters. also swear and use slang"

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

def tweetText():
    if tweetText == "":
        outputText.configure(text="Error: No tweet to post")
    else:
        client.create_tweet(text=tweetText)
        print(f"tweeted: {tweetText}")
        outputText.configure(text=f"✅ Tweet Posted")
        contextText.configure(text="")

def generateAiTextPrompt(prompt):
    global tweetText
    response = requests.post(API_URL, headers=HEADERS, json={"inputs": prompt})
    response_json = response.json()
    
    if isinstance(response_json, list) and response_json:
        raw_text = response_json[0].get("generated_text", "Error: No response")
        
        cleaned_text = raw_text.split("\n")[-1].strip()
        tweetText = cleaned_text
        outputText.configure(text=f"Generated Post: {cleaned_text}")
        return cleaned_text if cleaned_text else outputText.configure(text="Error: No response")
    
    outputText.configure(text="Error: No response")
    return "Error: No response"


def generateAndTweet():
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

def generateText():
    global context, prompt
    context = getRedditPosts(subreddits)
    print(context)
    contextText.configure(text=f"Context: {context}")
    text = generateAiTextPrompt(f"Heres a reddit post: {context}. {prompt}")
    print(f"Ai tweet: {text}")

def openSettings():
    settingsWindow = ctk.CTk()
    settingsWindow.title("Settings")
    settingsWindow.geometry("800x400")
    settingsWindow.resizable(False, False)

    settingsLabel = ctk.CTkLabel(settingsWindow, text="Settings")
    settingsLabel.pack(padx=10, pady=10)

    labelPrompt = ctk.CTkLabel(settingsWindow, text="Enter a new prompt:")
    labelPrompt.pack(padx=10, pady=5)
    editPrompt = ctk.CTkEntry(settingsWindow, width=600, height=5)
    editPrompt.pack(padx=10, pady=5)
    editPrompt.insert(0, prompt)
    submitPrompt = ctk.CTkButton(settingsWindow, text="Submit", command=lambda:newPrompt(editPrompt.get()))
    submitPrompt.pack(padx=10, pady=5)

    apiKeysButton = ctk.CTkButton(settingsWindow, text="API Keys", command=lambda:subprocess.Popen(["notepad", ".env"]))
    apiKeysButton.pack(padx=10, pady=10)

    apiKeysButtonExample = ctk.CTkButton(settingsWindow, text="Example API Keys Layout", command=lambda:subprocess.Popen(["notepad", ".env.example"]))
    apiKeysButtonExample.pack(padx=10, pady=10)

    settingsWindow.mainloop()

def newPrompt(newPrompt):
    global prompt
    prompt = newPrompt
    print(f"Prompt updated: {prompt}")

root = ctk.CTk()
root.title("Twitter Bot")
root.geometry("800x400")
root.resizable(False, False)

generateButton = ctk.CTkButton(root, text="Generate Post", command=generateText)
generateButton.pack(padx=10, pady=10)

tweetButton = ctk.CTkButton(root, text="Post", command=tweetText)
tweetButton.pack(padx=10, pady=10)

settingsButton = ctk.CTkButton(root, text="Settings", command=openSettings)
settingsButton.pack(padx=10, pady=10)

outputText = ctk.CTkLabel(root, text="", wraplength=600)
outputText.pack(padx=10, pady=10)

contextText = ctk.CTkLabel(root, text="", wraplength=600)
contextText.pack(padx=10, pady=10)

root.mainloop()