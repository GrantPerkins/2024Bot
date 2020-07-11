import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord import FFmpegPCMAudio
import asyncio
import filecmp
from time import time
from urllib.request import urlopen
import sys
from faqparser import FAQParser
import random

url = 'https://www.wpi.edu/we-are-wpi/frequently-asked-questions'
test_url = "https://www.wpi.edu/we-are-wpi"
TOKEN = ""

with open("token.txt", 'r') as f:
    TOKEN = f.readline()

bot = commands.Bot(">")

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
            "faq-updates": 731273029602115694,
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
        if message.content.lower().startswith(">help"):
            await message.channel.send("Bro literally fuck off")
        # elisabeth's dumb jokes
        if message.author.id == self.user_ids["elisabeth"] and any(
                [i in message.content for i in ["tf", "walk", "mods", "omg"]]):
            await message.channel.send("SHUT SHUT SHUT Elisabeth")
        #vector POG
        if "vector" in message.content.lower():
            await self.get_channel(self.channels["vc-text"]).send(file=discord.File("images/vector.jpg"))
        # emergency shutoff
        if message.content.startswith(">kill") and message.author.id == self.user_ids["grant"]:
            sys.exit()
        # play
        if message.content.startswith(">play") and message.author.id == self.user_ids["grant"]:
            channel = message.author.voice.channel
            if channel != None:
                member = random.choice(channel.members)
                print(member)
                print(self.get_channel(731339163424784486))
                member.move_to(self.get_channel(731339163424784486))
                source = FFmpegPCMAudio('images/scotland.mp3')
                voice = discord.utils.get(self.voice_clients, guild=message.guild)
                if voice and voice.is_connected():
                    await voice.move_to(channel)
                else:
                    voice = await channel.connect(self.get_channel(731339163424784486))
                player = voice.play(source)
        # FAQ update
        save_html("current.html")
        if not filecmp.cmp("faq.html", "current.html"):
            await self.get_channel(self.channels["faq-updates"]).send("WPI's FAQ changed. See:")
            await self.get_channel(self.channels["faq-updates"]).send(
                "https://www.wpi.edu/we-are-wpi/frequently-asked-questions")
            save_html("faq.html")



client = Client()
client.run(TOKEN)
