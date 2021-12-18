import discord
from discord.ext import commands
import json
import pickle
import os
import random
from dotenv import load_dotenv
from datetime import datetime, timedelta
from random import shuffle
import math
def get_prefix(client, message):
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]
os.chdir(r'C:\Users\uSeR\Desktop\Python_Work\Patrapol-Kulruchakorn')
client = commands.Bot(command_prefix = get_prefix)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
DATA_PATH = os.getenv('DATA_PATH') + "\database.txt"
CREATOR = os.getenv('CREATOR')
client.remove_command("help")

@client.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(title = "Help", description = "Use 'help' <command> for extended info")
    em.add_field(name = "General", value= "balance, changeprefix, serverlevel, clear")
    em.add_field(name="Games", value= "cflip, odds, blackjack")

    await ctx.send(embed = em)

@help.command()
async def balance(ctx):
    em = discord.Embed(title='balance',description = "Shows the amount of money you got.")
    em.add_field(name="*Syntax*", value = '<prefix>bal')
    await ctx.send(embed = em)
@help.command()
async def cprefix(ctx):
    em = discord.Embed(title='Change Prefix', description='Change Prefix on your server.')
    em.add_field(name="*Syntax*", value = '+cprefix <new prefix>')
    await ctx.send(embed = em)
@help.command()
async def cflip(ctx):
    em = discord.Embed(title='CoinFlip', description='Plays a game of coin flip.')
    em.add_field(name="*Syntax*", value = '+cflip <side> <amount>')
    await ctx.send(embed = em)
@help.command()
async def odds(ctx):
    em = discord.Embed(title='Odds', description='Plays a game of odds out. If you roll a one, you lose.')
    em.add_field(name="*Syntax*", value = '+odds <number range> <amount>')
    await ctx.send(embed = em)
@help.command()
async def blackjack(ctx):
    em = discord.Embed(title='BlackJack', description='Plays a game of BlackJack.Please make sure you have a text channel called "blackjack" and are in it.\n!blackjackhelp for further info.')
    em.add_field(name="*Syntax*", value = '!play <amount>')
    await ctx.send(embed = em)
@help.command()
async def serverlevel(ctx):
    em = discord.Embed(title='Server Level', description='Shows the current server level and experience points it currently has.')
    em.add_field(name="*Syntax*", value = '<prefix>serverlevel, <prefix>slvl')
    await ctx.send(embed = em)
@help.command()
async def clear(ctx):
    em = discord.Embed(title='Clear', description='Clear the text in the designated channel.')
    em.add_field(name="*Syntax*", value = '<prefix>clear')
    await ctx.send(embed = em)
dataFilename = "data.pickle"

class Data():
    def __init__(self, wallet,bank):
        self.wallet = wallet
        self.bank = bank
data = {}
meschecker = False
previd = ""
prevauthor = ""
prevcontent = 0


# Assumes there is a file in DATA_PATH called 'database.txt'
with open(DATA_PATH, 'r') as file:
    data = json.load(file)
print(data)

cards = {"A" : 1, "2" : 2, "3" : 3, "4" : 4, "5" : 5, "6" : 6, "7" : 7, "8" : 8, "9" : 9, "10" : 10, "J" : 10, "Q" : 10, "K" : 10}
sessions = {}
deck = []


#Events
@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    print(
        f'{client.user} is connected to the Discord!\n',
        f' server: {guild.name} \n  id: {guild.id}')

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

@client.event
async def on_message(message):
    global meschecker
    global previd
    global prevauthor
    global prevcontent
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)
    with open('serverlvl.json', 'r') as q:
        server = json.load(q)
    prefix = prefixes[str(message.guild.id)]
    if message.author == client.user:
        return
    elif message.content[:1] == prefix or message.content[:1] == "!":
        await update_data(server,str(message.guild.id))
        await client.process_commands(message)
    else:
        if meschecker == True and previd != message.author.id:
            member = loadMemData(message.author.id)
            member2 = loadMemData(previd)
            member.wallet += round(min((len(message.content)*(1+(server[str(message.guild.id)]['lvl']/10))),500))
            member2.wallet += round(min((prevcontent*(1+(server[str(message.guild.id)]['lvl']/10))),500))
            data[str(message.author)]['balance'] += round(min((len(message.content)*(1+(server[str(message.guild.id)]['lvl']/10))),500))
            data[str(prevauthor)]['balance'] += round(min((prevcontent*(1+(server[str(message.guild.id)]['lvl']/10))),500))
            saveMemData(message.author.id,member)
            saveMemData(previd, member2)
            json.dump(data, open(DATA_PATH, 'w'))
            total_exp = len(message.content) + prevcontent
            await add_exp(server, str(message.guild.id),total_exp)
            await level_up(server, str(message.guild.id), message.channel)
            previd = ""
            prevauthor = ""
            prevcontent = 0
            meschecker = False
        else:
            previd = message.author.id
            prevauthor = message.author
            prevcontent = len(message.content)
            meschecker = True
    
    with open('serverlvl.json', 'w') as q:
        json.dump(server, q)

    #Part of Blackjack in On_Message
    global sessions
    global deck
    channel = message.channel
    player = message.author
    editplay = loadMemData(player.id)
    
    #------------------------------------------------------------------#
    # Check if message was sent in the "blackjack" channel, or if the sender
    #    is the bot
    if "blackjack" not in channel.name or player == client.user:
        return
    #------------------------------------------------------------------#
    # Player name and message parsing setup
    name = f'{player}'
    msg = message.content if message.content.startswith('!gift') or message.content.startswith('!give') else message.content.lower()
    
    #------------------------------------------------------------------#
    if msg == '!blackjackhelp':
        embed = discord.Embed(title='List of Commands', desc='-', color=discord.Color.gold())
        embed.add_field(name='!play | !bet', value='!play <token amount>', inline=False)
        embed.add_field(name='!hit | !stand', value='!hit - be dealt another card\n!stand - lock in your hand', inline=False)

        # Separate !bal and !stats eventually
        embed.add_field(name='!bal | !stats | !balance', value='Shows player profile with current balance, W/L/T, and rank', inline=False)
        
        embed.add_field(name='!top | !leaderboard', value='Displays the top 4 players', inline=False)
        await channel.send(f"{player.mention}", embed=embed)
        return
    #------------------------------------------------------------------#
    elif msg.startswith('!') and name not in data and msg != '!create':
        await channel.send('Please create a blackjack account with "!create"')

    #------------------------------------------------------------------#
    elif msg == '!hit':
        if name in sessions:
            sessions[name]['player_hand'].append(deck.pop())
            dealer_hand = sumHand(sessions[name]['dealer_hand'])
            player_hand = sumHand(sessions[name]['player_hand'])
            if player_hand > 21:
                data[name]['balance'] -= sessions[name]['bet']
                editplay.wallet -= sessions[name]['bet']
                data[name]['losses'] += 1
                json.dump(data, open(DATA_PATH, 'w'))
                saveMemData(player.id,editplay)
                await channel.send(f"{player.mention}", embed=genEmbed("lose", 'LOSS', 'You lost!!!', color=discord.Color.red(), player=name))
                del sessions[name]

            elif player_hand == 21:
                while sumHand(sessions[name]['dealer_hand']) < 17:
                    sessions[name]['dealer_hand'].append(deck.pop())
                if sumHand(sessions[name]['dealer_hand']) == 21:
                    data[name]['ties'] += 1
                    await channel.send(f"{player.mention}", embed=genEmbed("tie", 'TIE!', 'Nobody wins. All bets returned.', player=name))
                else:
                    data[name]['wins'] += 1
                    data[name]['balance'] += sessions[name]['bet']
                    editplay.wallet += sessions[name]['bet']
                    json.dump(data, open(DATA_PATH, 'w'))
                    saveMemData(player.id, editplay)
                    await channel.send(f"{player.mention}", embed=genEmbed("win", ':tada: WIN!!! :tada:', 'You win!', color=discord.Color.green(), player=name))
                del sessions[name]
            
            else:
                await channel.send(f"{player.mention}", embed=genEmbed("play", 'Blackjack', 'Round Continued!', color=discord.Color.blue(), player=name))
        else:
            await channel.send(f"{player.mention} not currently in a game!")

    #------------------------------------------------------------------#
    elif msg == '!stand':
        if name in sessions:
            player_hand = sumHand(sessions[name]['player_hand'])
            while sumHand(sessions[name]['dealer_hand']) < 17:
                sessions[name]['dealer_hand'].append(deck.pop())
            dealer_hand = sumHand(sessions[name]['dealer_hand'])
            if (player_hand > dealer_hand and player_hand <= 21) or dealer_hand > 21:
                data[name]['wins'] += 1
                data[name]['balance'] += sessions[name]['bet']
                editplay.wallet += sessions[name]['bet']
                json.dump(data, open(DATA_PATH, 'w'))
                saveMemData(player.id, editplay)
                await channel.send(f"{player.mention}", embed=genEmbed("win", ':tada: WIN!!! :tada:', 'You win!', color=discord.Color.green(), player=name))
            elif player_hand < dealer_hand and dealer_hand <= 21:
                data[name]['losses'] += 1
                data[name]['balance'] -= sessions[name]['bet']
                editplay.wallet -= sessions[name]['bet']
                json.dump(data, open(DATA_PATH, 'w'))
                saveMemData(player.id, editplay)
                await channel.send(f"{player.mention}", embed=genEmbed("lose", 'LOSS', 'You lost!!!', color=discord.Color.red(), player=name))
            else:
                data[name]['ties'] += 1
                json.dump(data, open(DATA_PATH, 'w'))
                await channel.send(f"{player.mention}", embed=genEmbed("tie", 'TIE!', 'Nobody wins. All bets returned.', player=name))
            del sessions[name]
        else:
            await channel.send(f"{player.mention} not currently in a game!")

    elif msg in ('!bal', '!balance', '!stats'):
        await channel.send(f"{player.mention}", embed=genEmbed("stats", 'Your Profile', 'All stats.', player=name))
    
    #------------------------------------------------------------------#
    elif msg.startswith('!bet') or msg.startswith('!play'):
        # Verify session does not already exist
        if name not in sessions:
            # Verify proper command format: !bet <integer amount>
            if len(msg.split(' ')) == 2 and msg.split(' ')[1].isdigit():
                bet = int(msg.split(' ')[1])
                # Verify bet amount is legal: bet <= player balance and > 0
                if bet <= data[name]['balance'] and bet > 0:
                    sessions[name] = {"bet": bet, "player_hand": [], "dealer_hand": []}
                    if len(deck) < 75:
                        deck = genDeck()
                        print("Deck was shuffled.")
                    for _ in range(2):
                        sessions[name]['player_hand'].append(deck.pop())
                        sessions[name]['dealer_hand'].append(deck.pop())
                    dealer_hand = sumHand(sessions[name]['dealer_hand'])
                    player_hand = sumHand(sessions[name]['player_hand'])
                    
                    if player_hand == 21 and dealer_hand != 21:
                        # Payout player bet * 1.5 and add to balance. Increment Player win, Increment dealer loss.
                        data[name]['balance'] += int(sessions[name]['bet'] * 1.5)
                        editplay.wallet += int(sessions[name]['bet'] * 1.5)
                        sessions[name]['bet'] = int(sessions[name]['bet'] * 1.5)
                        data[name]['wins'] += 1
                        json.dump(data, open(DATA_PATH, 'w'))
                        saveMemData(player.id, editplay)
                        await channel.send(f"{player.mention}", embed=genEmbed("win", ':tada: :tada: WIN!!! :tada: :tada:', 'Natural! You win!', color=discord.Color.green(), player=name))
                        del sessions[name]

                    # Return player bet and do not change balance. Increment Player tie, Increment Dealer tie.
                    elif dealer_hand == 21 and dealer_hand == player_hand:
                        data[name]['ties'] += 1
                        json.dump(data, open(DATA_PATH, 'w'))
                        await channel.send(f"{player.mention}", embed=genEmbed("tie", 'TIE!', 'Nobody wins. All bets returned.', player=name))
                        del sessions[name]

                    else:
                        await channel.send(f"{player.mention}", embed=genEmbed("play", 'Blackjack', 'Round Started!', color=discord.Color.blue(), player=name))
                else:
                    await channel.send(f"{player.mention}", embed=genEmbed("error", 'Error!', f"You don't have {bet} tokens to bet!", color=discord.Color.orange()))
            else:
                await channel.send(f"{player.mention}", embed=genEmbed("error", 'Error!', 'Correct use is\n!bet <tokens>  OR !play <tokens>', color=discord.Color.orange()))
        else:
            await channel.send(f"{player.mention}", embed=genEmbed("error", 'Error!', 'Currently in a game!', color=discord.Color.orange()))
    
    
    #------------------------------------------------------------------#
    elif msg == '!leaderboard' or msg == '!top':
        if len(data.keys()) == 0:
            await channel.send(f"{player.mention}\nLeaderboard is currently empty.")
        line = '----------------------------------'
        await channel.send(f"{player.mention}", embed=genEmbed("leaderboard", ":chart_with_upwards_trend: :medal: Leaderboard :medal: :chart_with_upwards_trend:", f'{line}', color=discord.Color.purple()))
    
    #------------------------------------------------------------------#

    elif msg == '!create':
        editcurren = loadMemData(message.author.id)
        if name in data:
            await channel.send(f"{player.mention}", embed=genEmbed("error", 'Error!', 'Account already created!', color=discord.Color.orange()))
        else:
            data[name] = {'balance' : editcurren.wallet, 'lastjob': f'{datetime.utcnow()}'.split('.')[0], 'wins' : 0, 'losses' : 0, 'ties' : 0}
            json.dump(data, open(DATA_PATH, 'w'))
            saveMemData(message.author.id, editcurren)
            await channel.send(f"{player.mention}", embed=genEmbed("create", '\U00002660 Blackjack \U00002660', 'Account creation success!'))
    
    elif msg.startswith('!rigged'):
        await channel.send('Sue me.')

    # ==== DEBUGGING / CREATOR CONTROLS ==== #
    elif (msg == '!cheats' or msg == '!hacks') and name == CREATOR:
        if len(msg.split(' ')) == 2 and msg.split(' ')[1].isdigit():
            bet = int(msg.split(' ')[1])
            if bet <= 100000:
                data[name]['balance'] += bet
                json.dump(data, open(DATA_PATH, 'w'))
                await channel.send(f"{player.mention}", embed=genEmbed("job", 'Here you go creator!', f'You received {bet} tokens', color=discord.Color.green(), player=name))

    elif msg == '!quit' and name == CREATOR:
        del sessions[name]

    elif msg == '!next' and name == CREATOR:
        await channel.send(f"{player.mention} The next 2 cards are {deck[-1]} and {deck[-2]}")

    elif msg.startswith('!disconnect') and name == CREATOR:
        sessions.clear()
        json.dump(data, open(DATA_PATH, 'w'))
        await client.close()
    
    elif msg.startswith('!deleteacc') and name == CREATOR:
        await channel.send('f"{player.mention}, your account has been deleted."')
        data.pop(name)
    return

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

@client.command(aliases = ['slevel', 'slvl', 'serlvl'])
async def serverlevel(message):
    with open("serverlvl.json",'r') as f:
        server = json.load(f)
    level = server[str(message.guild.id)]['lvl']
    curexp = server[str(message.guild.id)]['exp']
    lvlcap = (int(level)+1) ** 8
    await message.channel.send(f'The server is level {level}\n  {curexp}/{lvlcap}')

@client.command()
async def clear(ctx, amount= 10):
    await ctx.channel.purge(limit=amount)




@client.command()
async def cflip(message, side, amount):
    gameList = ["head", "tail"]
    player = loadMemData(message.author.id)
    if int(amount) > player.wallet or int(amount) > data[str(message.author)]['balance']:
         await message.channel.send("insufficient amount")
    else:
        outcome = random.choice(gameList)
        if side == outcome:
            player.wallet += amount
            data[str(message.author)]['balance'] += amount
            json.dump(data, open(DATA_PATH, 'w'))
            await message.channel.send(f"You win {amount} coins!\nResult:{outcome}")
        else:
            player.wallet -= amount
            data[str(message.author)]['balance'] -= amount
            json.dump(data, open(DATA_PATH, 'w'))
            await message.channel.send(f"You lose {amount} coins...\nResult:{outcome}")
    saveMemData(message.author.id, player)

@client.command()
async def odds(message,num,amount):
    number = random.randint(1,int(num))
    player = loadMemData(message.author.id)
    if int(amount) > player.wallet:
        await message.channel.send("insufficient amount")
    else:        
        if number == 1:
            player.wallet -= int(amount)
            data[str(message.author)]['balance'] -= int(amount)
            await message.channel.send(f"You rolled {number}. Unlucky!")
        else:
            earn = math.ceil(int(amount) ** (1/int(num)))
            player.wallet += earn
            data[str(message.author)]['balance'] += earn
            await message.channel.send(f'You rolled {number}, and earned {earn} coins.')
    saveMemData(message.author.id, player)
    json.dump(data, open(DATA_PATH, 'w'))

@client.command(alias = ['give','gift'])
async def send(message,amount):
    global previd
    global prevauthor

    sender = loadMemData(message.author.id)
    reciever = loadMemData(previd)
    reciever.wallet += int(amount)
    sender.wallet -= int(amount)
    data[str(message.author)]['balance'] -= int(amount)
    data[str(prevauthor)]['balance'] += int(amount)
    await message.channel.send(f'{amount} has been sent to {prevauthor}.')
    saveMemData(message.author.id, sender)
    saveMemData(previd, reciever)
    json.dump(data, open(DATA_PATH, 'w'))



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
    
async def update_data(server,guild):
    if not guild in server:
        server[guild] = {}
        server[guild]['exp'] = int(0)
        server[guild]['lvl'] = 1

async def add_exp(server, guild, exp):
    server[guild]['exp'] += exp

async def level_up(server, guild, channel):
    experience = server[guild]['exp']
    lvl_str = server[guild]['lvl']
    lvl_end = int(experience ** (1/8))

    if lvl_str < lvl_end:
        await channel.send(f'The server has leveled up!\n The current level is {lvl_end}.')
        server[guild]['lvl'] = lvl_end



#BLACKJACK
#------------------------------------------------------------------#
# *****This function can be streamlined more... TODO For future build
def genEmbed(type, title, desc, msg="", color=discord.Color.blurple(), player=None):
    global sessions
    embed = discord.Embed(
                        title = title,
                        description = desc,
                        color = color
                        )
    if type == "create":
        embed.add_field(name='\U0001F4B0          \U0001F4B0', value="", inline=False)
        embed.set_footer(text='Type !help or !assist if you\'re lost!')
    elif type == 'play' or type == "win" or type == "lose":
        field_name = {'play' : 'Bet Amount', 'win' : 'Amount Won', 'lose' : 'Amount Lost'}
        footer = {'play' : '!hit or !stand', 'win' : 'Blackjack prodigy!', 'lose' : 'Better luck next time!'}
        embed.add_field(name=field_name[type], value=f":coin: {sessions[player]['bet']} :coin:", inline=False)
        embed.add_field(name='Balance', value=f"\U0001F4B0 {data[player]['balance']} \U0001F4B0", inline=False)
        embed.add_field(name='Player Hand', value=f"{' - '.join([i for i in sessions[player]['player_hand']])}", inline=True)
        embed.add_field(name=' :black_large_square:', value=' :black_large_square:', inline=True)
        dealer_hand = f"{sessions[player]['dealer_hand'][0]} - \U0001F0CF" if type == 'play' else f"{' - '.join([i for i in sessions[player]['dealer_hand']])}"
        embed.add_field(name='Dealer Hand', value=dealer_hand, inline=True)
        embed.set_footer(text=footer[type])
    elif type == "tie":
        embed.add_field(name='Balance', value=f"\U0001F4B0 {data[player]['balance']} \U0001F4B0", inline=False)
        embed.add_field(name='Player Hand', value=f"{' - '.join([i for i in sessions[player]['player_hand']])}", inline=True)
        embed.add_field(name=' :black_large_square:', value=' :black_large_square:', inline=True)
        embed.add_field(name='Dealer Hand', value=f"{' - '.join([i for i in sessions[player]['dealer_hand']])}", inline=True)
        embed.set_footer(text='Bet again!')
    elif type == "stats":
        embed.add_field(name='Balance', value=f"\U0001F4B0 {data[player]['balance']} \U0001F4B0", inline=False)
        embed.add_field(name='Wins', value=f"{data[player]['wins']}", inline=True)
        embed.add_field(name='Losses', value=f"{data[player]['losses']}", inline=True)
        embed.add_field(name='Ties', value=f"{data[player]['ties']}", inline=True)
        embed.add_field(name='Rank', value=f"Not yet implemented", inline=False)
        embed.set_footer(text='!help or !assist if you\'re lost')
    elif type == "leaderboard":
        leaderboard = sorted([(k, v['balance'], v['wins']) for k,v in data.items()], key=(lambda x: (x[1],x[2])), reverse=True)
        if len(leaderboard) > 4:
            leaderboard = leaderboard[0:4]
        for i, v in enumerate(leaderboard):
            emoji = {0 : ':first_place:', 1 : ':second_place:', 2: ':third_place:'}
            i = emoji[i] if i in emoji else f"#{i+1}"
            embed.add_field(name=f"{i} :  {v[0][:-5]}", value=f"{v[1]}", inline=False)
        embed.set_footer(text='!help or !assist if you\'re lost')
    elif type == 'job':
        embed.add_field(name='New Balance', value=f"\U0001F4B0 {data[player]['balance']} \U0001F4B0", inline=False)
        embed.set_footer(text='!help or !assist if you\'re lost')
    return embed

#------------------------------------------------------------------#
# Generates a standard blackjack deck. Consists of 6 packs of 52 ct cards, shuffled.
def genDeck():
    deck = []
    # Generate a deck of 6 packs
    for _ in range(6):
        pack = []
        # Generate each pack
        for i in range(4):
            pack += cards.keys()
            shuffle(pack)
        deck += pack
        shuffle(deck)
    return deck

#------------------------------------------------------------------#\
# Calculates the value of a hand according to Blackjack rules
def sumHand(hand):
    hand_sum = 0
    aces = 0
    for i in hand:
        if i != 'A':
            hand_sum += cards[i]
        else:
            aces += 1
    # Handle aces
    for i in range(aces):
        if hand_sum + 11 <= 21:
            hand_sum += 11
        else:
            hand_sum += 1
    return hand_sum

client.run(TOKEN)