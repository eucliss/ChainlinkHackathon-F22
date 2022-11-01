# This example requires the 'members' privileged intent to use the Member converter
# and the 'message_content' privileged intent for prefixed commands.

# Using https://github.com/Pycord-Development/pycord/blob/master/examples/basic_bot.py
# Using the above link to bootstrap a discord bot

from email.errors import CloseBoundaryNotFoundDefect
import random
from typing_extensions import get_overloads

from coordinator import Coordinator
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


coord = Coordinator(
    database='DiscordTesting2'
)

CONFIG = {
    'state': 'UNINITIALIZED',
    'customerId': None,
    'invoiceAddr': None,
    'assets': None,
    'erc20': None,
    'erc721': None,
    'assetTypes': None,
    'nftIdentifier': None,
}

ItemTypes = {
    'NATIVE': 0,
    'ERC20': 1,
    'ERC721': 2,
    'ERC1155': 3,
    'NONE': 4
}

@bot.event
async def on_ready():
    print(CONFIG)
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def init(ctx: commands.Context):
    coord.restart()
    global CONFIG
    print("Entered the initialize function, setting state.")
    if CONFIG['state'] == 'INITIALIZED':
        await ctx.send(f'ERROR: Already initialized')
        return
    
    print("Registering a new customer")
    event = coord.registerCustomer()
    invoiceAddr = event['customer']
    customerId = 'CUST1'
    print(f'Registered a new customer: {customerId}, {invoiceAddr}')

    success, erc20, _, _ = coord.connector.deployContract('GameERC20')
    if not success:
        await ctx.send(f'Failed to deploy ERC20 contract')    
    print(f'Successfully deployed ERC20: {erc20}')
    success, erc721, _, _ = coord.connector.deployContract('GameERC721')
    if not success:
        await ctx.send(f'Failed to deploy ERC721 contract')    
    print(f'Successfully deployed ERC721: {erc721}')

    print('Registering assets')
    assets = coord.registerAssets(
        invoiceAddr,
        [erc20, erc721],
        [ItemTypes['ERC20'], ItemTypes['ERC721']]
    )['updatedContracts']
    print(f'Successfully registered assets: {assets}')


    erc20 = {
        'address': erc20,
        'identifier': coord.assetStore.getAssetIdentifier(erc20)
    }

    erc721 = {
        'address': erc721,
        'identifier': coord.assetStore.getAssetIdentifier(erc721)
    }

    CONFIG = {
        'state': 'INITIALIZED',
        'customerId': customerId,
        'invoiceAddr': invoiceAddr,
        'assets': assets,
        'erc20': erc20,
        'erc721': erc721,
        'assetTypes': [ItemTypes['ERC20'], ItemTypes['ERC721']],
        'nftIdentifier': 0
    }
    print(f'Config is set: {CONFIG}')
    await ctx.send(f'Customer ({customerId}) created at {invoiceAddr}')
    await ctx.send(f'Assets added: {assets}')

@bot.command()
async def register(ctx: commands.Context):
    print(f'Registering User: {str(ctx.author)}')
    userId, _, msg = coord.userStore.addUser(str(ctx.author))
    await ctx.send(f'Successfully registered user: {str(ctx.author)} ({userId})')

@bot.command()
async def balance(ctx: commands.Context):
    print(f'Getting balance of user: {str(ctx.author)}')
    userId, _, msg = coord.userStore.addUser(str(ctx.author))
    assets = coord.userStore.getUserAssets(str(ctx.author))
    assetMap = {
        'ASS1': 'Token',
        'ASS2': 'NFT'
    }
    try:
        for asset in assets:
            await ctx.send(f'{assetMap[asset]} balance: {assets[asset]["amount"]}')
    except:
        await ctx.send(f'You have no assets')

@bot.command()
async def checkChain(ctx: commands.Context):
    print(f'Getting custodial balances')
    tokenAmount = coord.connector.getCustodialBalance(CONFIG['erc20']['address'], "GameERC20")
    nftAmount = coord.connector.getCustodialBalance(CONFIG['erc721']['address'], "GameERC721")
    await ctx.send(f'The custodial wallet has {tokenAmount} Tokens (ERC20)')
    await ctx.send(f'The custodial wallet has {nftAmount} NFTs (ERC721)')

@bot.command()
async def getBill(ctx: commands.Context):
    print(f'Getting the current bill balance')
    due = coord.getCustomerBill(customerId='CUST1')
    await ctx.send(f'Your outstanding fee is: {due} gwei')


@bot.command()
async def roll(ctx: commands.Context):
    print(f'Rolling the dice ... ')
    num = random.random() * 10000
    num = num % 6
    print(f'Got number: {num}')
    userId = coord.userStore.getUserId(str(ctx.author))
    print(f'Got UserId: {userId}')
    if 0 <= num <= 2:
        print('Number in between 0-2, giving 100 ERC20')
        event = coord.mintAssets(
            [{
                'itemType': ItemTypes['ERC20'],
                'token': CONFIG['erc20']['address'],
                'identifier': 0,
                'amount': 100
            }],
            [str(ctx.author)]
        )
        print(f'Added assets to user: 100  tokens')
        await ctx.send(f'You\'ve won 100 Tokens!!')

    if 2 < num <= 4:
        print('Number in between 3-4, giving 1000 ERC20')
        event = coord.mintAssets(
            [{
                'itemType': ItemTypes['ERC20'],
                'token': CONFIG['erc20']['address'],
                'identifier': 0,
                'amount': 1000
            }],
            [str(ctx.author)]
        )
        print(f'Added assets to user: 1000  tokens')
        await ctx.send(f'You\'ve won 1000 Tokens!!')
    if 4 < num <= 6:
        print('Number equal to 5, giving 1000 ERC20 and 1 ERC721')
        event = coord.mintAssets(
            [{
                'itemType': ItemTypes['ERC20'],
                'token': CONFIG['erc20']['address'],
                'identifier': 0,
                'amount': 1000
            }],
            [str(ctx.author)]
        )
        print(f'Added assets to user: 1000  tokens')
        event = coord.mintAssets(
            [{
                'itemType': ItemTypes['ERC721'],
                'token': CONFIG['erc721']['address'],
                'identifier': CONFIG['nftIdentifier'],
                'amount': 1
            }],
            [str(ctx.author)]
        )
        nftId = CONFIG['nftIdentifier']
        CONFIG['nftIdentifier'] = CONFIG['nftIdentifier'] + 1
        print(f'Added assets to user: NFT{nftId}')
        await ctx.send(f'You\'ve won 1000 Tokens and NFT #{nftId}!!')
    userAssets = coord.userStore.getUserAssets(str(ctx.author))
    print(f'Users updated assets: {userAssets}')

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

bot.run(token)