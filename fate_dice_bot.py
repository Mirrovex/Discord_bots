#https://www.youtube.com/watch?v=DEqrCI1018I

import discord
from discord.ext import commands
import random

import json


with open("./token.json") as file:
    TOKEN = json.load(file)["fate"]


client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('Bot jest gotowy')


@client.command()
async def roll(ctx): #.roll = komenda
    username = ctx.message.author.name
    txt = ''
    wynik = 0
    lista = ['[-]', '[ ]', '[+]', '[-]', '[ ]', '[+]']
    for x in range(4):
        r = random.randint(0,5)
        dice = lista[r]
        txt += dice
        txt += ' '

        if dice == '[-]':
            wynik -= 1
        elif dice == '[+]':
            wynik += 1

    if wynik >= 0:
        #await ctx.send(f"""```css\n{username}: {txt}= (+{str(wynik)})```""")
        await ctx.send(f'**{username}**: {txt}= (+{str(wynik)})')
    elif wynik < 0:
        #await ctx.send(f"""```css\n{username}: {txt}= ({str(wynik)})```""")
        await ctx.send(f'**{username}**: {txt}= ({str(wynik)})')


client.run(TOKEN)