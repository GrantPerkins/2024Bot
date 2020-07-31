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
import tflite_runtime.interpreter as tflite
import numpy as np
from PIL import Image
import requests

url = 'https://www.wpi.edu/we-are-wpi/frequently-asked-questions'
test_url = "https://www.wpi.edu/we-are-wpi"
TOKEN = ""

with open("token.txt", 'r') as f:
    TOKEN = f.readline()

bot = commands.Bot(">")


def load_labels(filename):
  with open(filename, 'r') as f:
    return [line.strip() for line in f.readlines()]

def save_html(filename):
    response = urlopen(url)
    if response.getheader('Content-Type').split(";")[0] == 'text/html':
        html_bytes = response.read()
        html_string = html_bytes.decode("utf-8")
        parser = FAQParser()
        parser.feed(html_string)
        with open(filename, "w+") as f:
            f.writelines(parser.data)
        return parser.data


class Client(discord.Client):
    def __init__(self):
        super().__init__()
        self.voice = None
        self.channel = None
        self.roles = {
            "mod": 699644834629288007,
            "hipster": 710844902585532416,
            "bots": 699646033323622540
        }
        self.user_ids = {
            "elisabeth": 696911603068829836,
            "grant": 454052089979600897
        }
        self.channels = {
            "faq-updates": 731273029602115694,
            "general": 699643028121452676,
            "vc-text": 706619592935735316
        }
        self.interpreter = tflite.Interpreter("mobilenet_v1_1.0_224_quant.tflite")
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        floating_model = self.input_details[0]['dtype'] == np.float32

        # NxHxWxC, H:1, W:2
        height = self.input_details[0]['shape'][1]
        width = self.input_details[0]['shape'][2]

    async def on_ready(self):
        print('Logged on as', self.user)
        # reset("faq.html")

    async def on_message(self, message):

        if message.author == self.user:
            return
        if random.randint(0, 450) == 1:
            await message.channel.send(random.choice(
                ["hey. fuck you.", "you are shit.", "sugma dick", "bloody wanker", "?ban @you, stupid bitch"]))
        # ping
        if message.content == '>ping':
            before = time()
            await message.channel.send('Pong!')
            ms = (time() - before) * 1000
            await message.channel.send('Ping took: {}ms'.format(int(ms)))
            print("ping")
        # send as mod
        if message.content.startswith(">send") and any([role.id == self.roles["mod"] for role in message.author.roles]):
            cmd, channel, *text = message.content.split()
            text = " ".join(text)
            channel = self.get_channel(int(channel[2:-1]))
            await channel.send(text)
        if message.content.lower().startswith(">help"):
            await message.channel.send("Bro literally fuck off")
        # emergency shutoff
        if message.content.startswith(">kill") and message.author.id == self.user_ids["grant"]:
            sys.exit()
        # play
        if len(self.get_channel(731339163424784486).members) == 1:
            await self.voice.disconnect()
            self.voice = None
            print("disconnecting")

        if message.content.startswith(">play") and any(
                [role.id == self.roles["mod"] or role.id == self.roles["hipster"] for role in message.author.roles]):
            channel = message.author.voice.channel
            if channel != None:
                is_bot = lambda i: any([self.roles["bots"] == role.id for role in i.roles])
                try:
                    member = random.choice([i for i in channel.members if not is_bot(i)])
                    print("playing")
                    source = FFmpegPCMAudio('images/scotland.mp3')
                    self.voice = discord.utils.get(self.voice_clients, guild=message.guild)
                    if self.voice and self.voice.is_connected():
                        pass
                    else:
                        self.voice = await self.get_channel(731339163424784486).connect()
                        self.voice.play(source)
                        await member.move_to(self.get_channel(731339163424784486))
                except:
                    pass

        if message.content.startswith(">wtf"):
            if len(message.attachments) > 0:
                path = message.attachments[0].url
                r = requests.get(path)
                name = path.split('/')[-1]
                with open(name,'wb') as f:
                    f.write(r.content)
                floating_model = self.input_details[0]['dtype'] == np.float32

                # NxHxWxC, H:1, W:2
                height = self.input_details[0]['shape'][1]
                width = self.input_details[0]['shape'][2]
                img = Image.open(name)
                if name.endswith("png"):
                    img.save("test.jpg")
                    img = Image.open("test.jpg")

                img = img.resize((width, height))


                # add N dim
                input_data = np.expand_dims(img, axis=0)

                if floating_model:
                    input_data = (np.float32(input_data) - 127.5) / 127.5

                self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
                self.interpreter.invoke()

                start_time = time()
                self.interpreter.invoke()
                stop_time = time()

                output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
                results = np.squeeze(output_data)

                top_k = results.argsort()[-5:][::-1]
                labels = load_labels("labels_mobilenet_quant_v1_224.txt")
                await message.channel.send("It's a {}.".format(labels[top_k[0]])+' time: {:.3f}ms'.format((stop_time - start_time) * 1000))


client = Client()
client.run(TOKEN)
