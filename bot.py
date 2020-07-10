import discord
import filecmp
from time import time
from urllib.request import urlopen
import sys
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
    def __init__(self):
        super().__init__()
        self.roles = {
            "mod": 699644834629288007
        }
        self.user_ids = {
            "elisabeth": 731214087740063886,
            "grant": 454052089979600897
        }
        self.channels = {
            "faq-updates": 731214087740063886,
            "general": 699643028121452676,
            "vc-text": 706619592935735316
        }

    async def on_ready(self):
        print('Logged on as', self.user)
        # reset("faq.html")

    async def on_message(self, message):
        if message.author == self.user:
            return

        # ping
        if message.content == '>ping':
            before = time()
            await message.channel.send('Pong!')
            ms = (time() - before) * 1000
            await message.channel.send('Ping took: {}ms'.format(int(ms)))
        # send as mod
        if message.content.startswith(">send") and any([role.id == self.roles["mod"] for role in message.author.roles]):
            cmd, channel, *text = message.content.split()
            text = " ".join(text)
            channel = self.get_channel(int(channel[2:-1]))
            await channel.send(text)
        # elisabeth's dumb jokes
        if message.author.id == self.user_ids["elisabeth"] and any(
                [i in message.content for i in ["tf", "walk", "mods"]]):
            await message.channel.send("SHUT SHUT SHUT Elisabeth")
        #vector POG
        if "vector" in message.content.lower():
            await self.get_channel(self.channels["vc-text"]).send(file=discord.File("images/vector.jpg"))
        # emergency shutoff
        if message.content.startswith(">kill") and message.author.id == self.user_ids["grant"]:
            sys.exit()
        # FAQ update
        save_html("current.html")
        if not filecmp.cmp("faq.html", "current.html"):
            await self.get_channel(self.channels["faq-updates"]).send("WPI's FAQ changed. See:")
            await self.get_channel(self.channels["faq-updates"]).send(
                "https://www.wpi.edu/we-are-wpi/frequently-asked-questions")


client = Client()
client.run(TOKEN)
