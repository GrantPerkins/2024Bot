import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord import FFmpegPCMAudio
import asyncio
import filecmp
from time import time
from urllib.request import urlopen
import sys
import random
import tflite_runtime.interpreter as tflite
import numpy as np
from PIL import Image
import requests
import os
import smtplib
import ssl
import json

from datetime import date

url = 'https://www.wpi.edu/we-are-wpi/frequently-asked-questions'
test_url = "https://www.wpi.edu/we-are-wpi"
TOKEN = ""

with open("token.txt", 'r') as f:
    TOKEN = f.readline()

bot = commands.Bot(">")


def load_labels(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]


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
            "grant": 454052089979600897
        }
        self.channels = {
            "faq-updates": 731273029602115694,
            "general": 699643028121452676,
            "vc-text": 706619592935735316,
            "hipster-text": 730191680082542732,
            "bookings": 771056191542919188
        }
        self.interpreter = tflite.Interpreter("mobilenet_v1_1.0_224_quant.tflite")
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        floating_model = self.input_details[0]['dtype'] == np.float32

        # NxHxWxC, H:1, W:2
        height = self.input_details[0]['shape'][1]
        width = self.input_details[0]['shape'][2]
        self.email_text = """\
From: gcperk20@gmail.com
To: {to}
Subject: [Dine On Campus] Reservation Confirmation

Dear {name},

Thank you for making a reservation through Dine On Campus. 

You are confirmed at:

Location: {hall}
Date: {date}
Time: {time}

You can cancel your reservation any time by logging into your account using the Dine On Campus mobile app or website. 

You can login at https://dineoncampus.com/wpi/login

Thank you!

------------------------------------ 

This email is sent from an automated inbox and is not checked for replies.

"""

    async def on_ready(self):
        print('Logged on as', self.user)

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
        if message.content.startswith(">send") and message.author.id == self.user_ids["grant"]:
            cmd, channel, *text = message.content.split()
            text = " ".join(text)
            channel = self.get_channel(int(channel[2:-1]))
            await channel.send(text)
        if message.content.lower().startswith(">help"):
            await message.channel.send("Bro literally fuck off")
        # emergency shutoff
        if message.content.startswith(">kill") and message.author.id == self.user_ids["grant"]:
            sys.exit()
        if message.content.startswith(">wtf"):
            if len(message.attachments) > 0:
                path = message.attachments[0].url
                r = requests.get(path)
                name = path.split('/')[-1]
                with open(name, 'wb') as f:
                    f.write(r.content)
                floating_model = self.input_details[0]['dtype'] == np.float32

                # NxHxWxC, H:1, W:2
                height = self.input_details[0]['shape'][1]
                width = self.input_details[0]['shape'][2]
                img = Image.open(name)
                if name.endswith("png"):
                    img = img.convert("RGB")
                    img.save("test.jpg")
                    img = Image.open("test.jpg")
                    os.remove(name)
                    name = "test.jpg"

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
                answer = labels[top_k[0]]
                confidence = max(results) * 100 / 255.0
                print(results)
                await message.channel.send(
                    "It's a {}.".format(answer) + ' time: {:.3f}ms, confidence of answer: {:08.6f}%'.format(
                        (stop_time - start_time) * 1000, confidence))
                await message.channel.send(message.author.mention)
                os.remove(name)

        if message.content.startswith(">book") and message.channel.id == self.channels["bookings"]:
            if message.content.split()[1] == "how":
                await message.channel.send(
                    "First, config future bookings. Run `>config {your name} {your email}`.\n Then, book for today. Run `>book {where ya wanna eat (m, cc, gh, foisie, or smthn else)} {time}`")
            else:
                try:
                    text = message.content.split()[1:]
                    name, location, booking, email = None, None, None, None
                    try:
                        with open("config.json", 'r') as f:
                            d = json.load(f)
                            location, booking = text
                            id = str(message.author.id)
                            name = d[id][0]
                            email = d[id][1]
                    except Exception as e:
                        await message.channel.send(
                            "issue with config. try re-running >config {name} {email}. " + str(e))
                    if location.lower().startswith("m"):
                        location = "Morgan Dining Hall"
                    elif location.lower().startswith("c"):
                        location = "Campus Center Food Court"
                    elif location.lower().startswith("g"):
                        location = "Goat's Head Restaurant"
                    elif location.lower().startswith("f"):
                        location = "Foisie Cafe"
                    day = date.today().strftime("%A %B %d, %Y")
                    await message.channel.send(
                        "Email:{}\nLocation:{}\nName:{}\nTime:{}\nDay:{}".format(email, location, name, booking, day))
                    port = 465  # For SSL

                    # Create a secure SSL context
                    context = ssl.create_default_context()
                    gmail_user = "dineoncampu@gmail.com"
                    gmail_password = None
                    with open("pass.txt", 'r') as f:
                        gmail_password = f.readline().rstrip('\n')
                    sent_from = gmail_user

                    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                        print(gmail_user, gmail_password)
                        server.login(gmail_user, gmail_password)
                        server.sendmail(sent_from, email,
                                        self.email_text.format(to=email, hall=location, name=name, time=booking,
                                                               date=day))
                    await message.channel.send("Check your email.")
                except Exception as e:
                    await message.channel.send("ERROR " + str(e))
        if message.content.startswith(">config") and message.channel.id == self.channels["bookings"]:
            d = {}
            with open("config.json", 'r') as f:
                id = message.author.id
                text = message.content.split()[1:]
                name = text[0]
                email = text[1]
                try:
                    d = json.load(f)
                except:
                    pass
                d[id] = [name, email]
            with open("config.json", 'w+') as f:
                json.dump(d, f)
            await message.channel.send("Successful config.", name, email)


client = Client()
client.run(TOKEN)
