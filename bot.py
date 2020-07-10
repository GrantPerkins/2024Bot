import discord
import filecmp
from time import time
from urllib.request import urlopen

from faqparser import FAQParser

url = 'https://www.wpi.edu/we-are-wpi/frequently-asked-questions'
test_url = "https://www.wpi.edu/we-are-wpi"
TOKEN = ""

with open("token.txt", 'r') as f:
    TOKEN = f.readline()

def save_html(filename):
    response = urlopen(url)
    if response.getheader('Content-Type').split(";")[0] == 'text/html':
        html_bytes = response.read()
        html_string = html_bytes.decode("utf-8")
        parser = FAQParser()
        parser.feed(html_string)
        with open(filename, "w+") as f:
            f.writelines(parser.data)


class Client(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        # reset("faq.html")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content == '>ping':
            print(message.author)
            print(message.author.id)
            before = time()
            await message.channel.send('Pong!')
            ms = (time() - before) * 1000
            await message.channel.send('Ping took: {}ms'.format(int(ms)))

        if message.author.id == 696911603068829836 and any([i in message.content for i in ["tf", "walk", "mods"]]):
            await message.channel.send("SHUT SHUT SHUT Elisabeth")

        save_html("current.html")
        if not filecmp.cmp("faq.html", "current.html"):
            await self.get_channel(731214087740063886).send("WPI's FAQ changed. See:")
            await self.get_channel(731214087740063886).send("https://www.wpi.edu/we-are-wpi/frequently-asked-questions")


client = Client()
client.run(TOKEN)
