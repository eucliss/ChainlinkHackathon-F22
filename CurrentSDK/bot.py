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
import web3
import json

description = """
An example bot to showcase the discord.ext.commands extension module.
There are a number of utility commands being showcased here.
"""

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), description=description, intents=intents)

OWNER = "Smig#0682"
coord = ''
STAGE = os.getenv('STAGE')
if STAGE == 'dev':
    coord = Coordinator(
       database='DiscordTesting'
    )
if STAGE == 'goerli':
    coord = Coordinator(
        database='DiscordGoerli'
    )

CONFIG = {
    'state': 'UNINITIALIZED',
    'customerId': None,
    'invoiceAddr': None,
    'assets': None,
    'erc20': None,
    'erc721': None,
    'assetTypes': None,
    'nftIdentifier': None
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

# TODO:
# Set NFT and TOKEN addresses if we deploy through deploy script

@bot.command()
async def init(ctx: commands.Context):
    # coord.restart()
    global CONFIG
    print("Entered the initialize function, setting state.")
    if CONFIG['state'] == 'INITIALIZED':
        await ctx.send(f'ERROR: Already initialized')
        return
    
    print("Registering a new customer")
    # event = coord.registerCustomer()
    # invoiceAddr = event['customer'] # 0xB219C67312C6bd1d92084333119b4Acfe9cF66C8
    invoiceAddr = web3.Web3.toChecksumAddress("0xB219C67312C6bd1d92084333119b4Acfe9cF66C8")
    customerId = 'CUST1'
    print(f'Registered a new customer: {customerId}, {invoiceAddr}')

    # 0xeFa6168c8F63E5D1c44c49AE63423A151067Ddb6
    success, erc20, _, _ = coord.connector.deployContract('CurrentToken')
    # erc20 = web3.Web3.toChecksumAddress("0xeFa6168c8F63E5D1c44c49AE63423A151067Ddb6")
    # if not success:
        # await ctx.send(f'Failed to deploy ERC20 contract')    
    print(f'Successfully deployed ERC20: {erc20}')
    success, erc721, _, _ = coord.connector.deployContract('CurrentNFT')
    # 0x9996B76adF5df73f79510BF9C2ecD2da1cE01f8f
    # erc721 = web3.Web3.toChecksumAddress("0x236c18F34f5D896c78874DED429D9cDdec75Ef4a")
    # if not success:
    #     await ctx.send(f'Failed to deploy ERC721 contract')    
    print(f'Successfully deployed ERC721: {erc721}')

    print('Registering assets')
    assets = coord.registerAssets(
        invoiceAddr,
        [erc20, erc721],
        [ItemTypes['ERC20'], ItemTypes['ERC721']]
    )['updatedContracts']
    print(f'Successfully registered assets: {assets}')

    # res = coord.assetStore.addAssets(
    #     'CUST1', 
    #     [erc20, erc721],
    #     [ItemTypes['ERC20'], ItemTypes['ERC721']]
    # )
    # res = coord.assetStore.addAssets(
    #     'CUST1', 
    #     [erc721],
    #     [ItemTypes['ERC721']]
    # )
    # print(res)

    erc20 = {
        'address': erc20,
        'identifier': coord.assetStore.getAssetIdentifier(erc20)
    }

    erc721 = {
        'address': erc721,
        'identifier': coord.assetStore.getAssetIdentifier(erc721)
    }

    assets = [erc20, erc721]


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
async def saveState(ctx: commands.Context):
    if str(ctx.author) != OWNER:
        await ctx.send(f'You dont own me ... ')
    else:    
        global CONFIG
        with open('config_state.json', 'w') as outfile:
            json.dump(CONFIG, outfile)
        await ctx.send(f'Saved bot state')

@bot.command()
async def loadState(ctx: commands.Context):
    if str(ctx.author) != OWNER:
        await ctx.send(f'You dont own me ... ')
    else:
        global CONFIG
        with open('config_state.json', 'r') as f:
            CONFIG = json.load(f)
        await ctx.send(f'Loaded bot state')


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
    tokenAmount = coord.connector.getCustodialBalance(CONFIG['erc20']['address'], "CurrentToken")
    nftAmount = coord.connector.getCustodialBalance(CONFIG['erc721']['address'], "CurrentNFT")
    await ctx.send(f'The custodial wallet has {tokenAmount} Tokens (ERC20)')
    await ctx.send(f'The custodial wallet has {nftAmount} NFTs (ERC721)')

@bot.command()
async def getBill(ctx: commands.Context):
    print(f'Getting the current bill balance')
    due = coord.getCustomerBill(customerId='CUST1')
    await ctx.send(f'Your outstanding fee is: {due} gwei')

@bot.command()
async def setAddress(ctx: commands.Context, address):
    print(f'Setting user address')
    coord.userStore.addAddress(str(ctx.author), address)
    await ctx.send(f'Updated your adddress to {address}.')
    await ctx.send(f'All following winnings will be transfered directly to your address.')

@bot.command()
async def getUserObject(ctx: commands.Context):
    print(f'Setting user address')
    obj = coord.userStore.client.getRecord(
            {
                'username': str(ctx.author)
            },
        )
    await ctx.send(f'{obj[0]}')

@bot.command()
async def export(ctx: commands.Context):
    print(f'Exporting User Assets')
    success, _, msg = coord.exportAssets(str(ctx.author))
    if success:    
        await ctx.send(f'Successfully exported user assets')
    if not success:
        await ctx.send(f'Failed exporting user assets')
        if 'custodial' in msg:
            await ctx.send(f'Please execute !setAddress <your address> then try again.')

@bot.command()
async def chainBalance(ctx: commands.Context):
    print(f'Getting user balances')
    try:
        addr = coord.userStore.getUserAddress(str(ctx.author))
        if addr == coord.custodialAddress:
            await ctx.send(f'Your account is still custodial, please execute !setAddress <your address> and !export to export your assets.')
        else:
            tokenAmount = coord.connector.getUserBalance(
                addr,
                CONFIG['erc20']['address'], 
                "CurrentToken"
            )
            nftAmount = coord.connector.getUserBalance(
                addr,
                CONFIG['erc721']['address'], 
                "CurrentNFT"
            )
            await ctx.send(f'You own {tokenAmount} Tokens (ERC20)')
            await ctx.send(f'You own {nftAmount} NFTs (ERC721)')
    except:
        await ctx.send(f'Please register your address and export first. (!setAddress <address>, !export')

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
        # event = coord.mintAssets(
        #     [{
        #         'itemType': ItemTypes['ERC20'],
        #         'token': CONFIG['erc20']['address'],
        #         'identifier': 0,
        #         'amount': 1000
        #     },
        #     {
        #         'itemType': ItemTypes['ERC721'],
        #         'token': CONFIG['erc721']['address'],
        #         'identifier': CONFIG['nftIdentifier'],
        #         'amount': 1
        #     }],
        #     [str(ctx.author), str(ctx.author)]
        # )
        nftId = CONFIG['nftIdentifier']
        CONFIG['nftIdentifier'] = CONFIG['nftIdentifier'] + 1
        print(f'Added assets to user: NFT{nftId}')
        await ctx.send(f'You\'ve won 1000 Tokens and NFT #{nftId}!!')
    print(event)
    userAssets = coord.userStore.getUserAssets(str(ctx.author))
    print(f'Users updated assets: {userAssets}')

# @bot.command()
# async def registerCustomer(ctx: commands.Context):
#     coord.restart()
#     global CONFIG
#     print("Entered the initialize function, setting state.")
#     if CONFIG['state'] == 'INITIALIZED':
#         await ctx.send(f'ERROR: Already initialized')
#         return

#     print("Registering a new customer")
#     event = coord.registerCustomer()
#     invoiceAddr = event['customer']
#     customerId = 'CUST1'
#     CONFIG['invoiceAddr'] = invoiceAddr
#     CONFIG['state'] = 'INITIALIZED'
#     print(f'Registered a new customer: {customerId}, {invoiceAddr}')
#     await ctx.send(f'Customer ({customerId}) created at {invoiceAddr}')
    


# @bot.command()
# async def registerAssets(ctx: commands.Context, tokenAddress, nftAddress):
#     global CONFIG
#     print('Registering assets')
#     erc20 = web3.Web3.toChecksumAddress(tokenAddress)
#     erc721 = web3.Web3.toChecksumAddress(nftAddress)
#     assets = coord.registerAssets(
#         CONFIG['invoiceAddr'],
#         [erc20, erc721],
#         [ItemTypes['ERC20'], ItemTypes['ERC721']]
#     )['updatedContracts']
#     print(f'Successfully registered assets: {assets}')


#     erc20 = {
#         'address': erc20,
#         'identifier': coord.assetStore.getAssetIdentifier(erc20)
#     }

#     erc721 = {
#         'address': erc721,
#         'identifier': coord.assetStore.getAssetIdentifier(erc721)
#     }
#     CONFIG['erc20'] = erc20
#     CONFIG['erc721'] = erc721
#     CONFIG['assetTypes'] =  [ItemTypes['ERC20'], ItemTypes['ERC721']]
#     CONFIG['nftIdentifier'] = 0
#     CONFIG['assets'] = assets
#     await ctx.send(f'Assets added: {assets}')

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

bot.run(token)