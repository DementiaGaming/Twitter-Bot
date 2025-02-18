# Setup
Clone this repo with git clone
```
git clone DementiaGaming/Twitter-Bot
```
Install required packages with pip
```
pip install -r requirements.txt
```
Then set up Twitter API, Reddit API, and Huggingface API and put all your keys into a .env file (example can be found in the .env.example file)

At the bottom of the script (currently at line 80) there is a prompt that you can edit if you want a different output

There is also a subreddits list (somewhere) in the script that you can edit to include different subreddits

The script will tweet the output if there aren't any errors
