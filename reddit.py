import praw

with open("reddit.txt", "r") as f:
    id, secret, passw = [i.replace('\n', '') for i in f.readlines()]
print(id, secret, passw)
reddit = praw.Reddit(client_id=id,
                     client_secret=secret,
                     password=passw,
                     user_agent="testscript by /u/TenseOrBoard",
                     username="WPI2024")
print(reddit.user.me())