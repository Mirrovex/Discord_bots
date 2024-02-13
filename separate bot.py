import discord
from discord.ext import commands
import asyncio

import json

client = commands.Bot(command_prefix = '.')
task = None
info_list = []
czas = 60*8 #oddzielnie jest co 8 min (60*8)


with open("./token.json") as file:
    TOKEN = json.load(file)["separate"]


async def separate(ctx, msg):
    if msg != '':
        message = msg.split(';')
        x = 0
        for line in message:
            await ctx.send(line)
            x += 1

            if x == len(message):
                info = await ctx.send('Wyslano: ' + str(x) + '/' + str(len(message)))
                info_list.append(info)
                await asyncio.sleep(10)
                await info.delete()
                info_list.clear()
                break

            info = await ctx.send('Wyslano: ' + str(x) + '/' + str(len(message)) + ', Czas: 0/' + str(czas))
            info_list.append(info)

            for s in range(czas):
                await asyncio.sleep(1)
                await info.edit(content='Wyslano: ' + str(x) + '/' + str(len(message)) + ', Czas: ' + str(s+1) + '/' + str(czas))

            #await asyncio.sleep(czas)

            await info.delete()
            info_list.clear()

@client.event
async def on_ready():
    print('Bot jest gotowy')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=".msg"))

@client.command()
async def msg(ctx, *, msg): #.msg = komenda
    global task
    await ctx.message.delete()

    if msg != 'stop':
        task = client.loop.create_task(separate(ctx, msg))
    else:
        task.cancel()
        task = None
        await info_list[0].edit(content='Anulowano')
        await asyncio.sleep(10)
        await info_list[0].delete()
        info_list.clear()


client.run(TOKEN)