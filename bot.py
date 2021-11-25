import discord
from discord.ext import commands
import json
import pickle
import os
def get_prefix(client, message):
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix = get_prefix)

dataFilename = "data.pickle"

class Data():
    def __init__(self, wallet):
        self.wallet = wallet

#Events
@client.event
async def on_ready():
    print("Bot is ready.")

@client.event
async def on_guild_join(guild):
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '+'

    with open('prefixes.json','w') as f:
        json.dump(prefixes, f)

@client.event
async def on_guild_remove(guild):
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)
        
    prefixes.pop(str(guild.id))

    with open('prefixes.json','w') as f:
        json.dump(prefixes, f)


#Commands
@client.command(aliases = ['cp', 'changeprefix'])
async def cprefix(ctx, prefix):
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)
        
    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json','w') as f:
        json.dump(prefixes, f)

    await ctx.send(f'Prefix has been change to {prefix}')

@client.command(aliases = ['balance','money','mon','cash'])
async def bal(message):
    memData = loadMemData(message.author.id)
    embedVar = discord.Embed(title="{member}'s Balance".format(member = message.author.display_name))
    embedVar.add_field(name="Wallet", value=str(memData.wallet))

    await message.channel.send(embed=embedVar)




#Functions
def loadData():
    if os.path.isfile(dataFilename):
        with open(dataFilename,"rb") as file:
            return pickle.load(file)
    else:
        return dict()

def loadMemData(memberID):
    data = loadData()

    if  memberID not in data:
        return Data(0,0)
    return data[memberID]

def saveMemData(memberID, memData):
    data = loadData()
    data[memberID] = memData

    with open(dataFilename,"wb") as file:
        pickle.dump(data, file)

client.run('OTEzNDcwNzUzNjE2MzE0Mzc4.YZ-97w.6nx67sHRKzmtLCAMJjoolkCNEUw')