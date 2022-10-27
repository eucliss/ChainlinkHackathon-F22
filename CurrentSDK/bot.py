# This example requires the 'members' privileged intent to use the Member converter
# and the 'message_content' privileged intent for prefixed commands.

# Using https://github.com/Pycord-Development/pycord/blob/master/examples/basic_bot.py
# Using the above link to bootstrap a discord bot

from email.errors import CloseBoundaryNotFoundDefect
import random
from typing_extensions import get_overloads

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

description = """
An example bot to showcase the discord.ext.commands extension module.
There are a number of utility commands being showcased here.
"""

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), description=description, intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.event
async def on_message(ctx: commands.Context):
    print(f'Message from {ctx.author}: {ctx.content}, {ctx}')
    print(ctx.channel.id)

# Register as a customer

# Register assets

# Register with assets

# Distribute Assets

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

bot.run(token)