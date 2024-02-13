#from keep_alive import keep_alive
import discord
from discord import app_commands, ui, utils
import os
import asyncio


TOKEN = "token"


all_guilds = []

class aClient(discord.Client):
    def __init__(self):
        super().__init__(intents = discord.Intents.all())
        self.synced = False
    
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            global all_guilds
            for guild in client.guilds:
                all_guilds.append(guild)
            await tree.sync()
            self.synced = True
        
        print("Bot jest gotowy")


client = aClient()
tree = app_commands.CommandTree(client)

@tree.command(name='pokaż', description='Pokazuje użytkowników, którzy mają podane role', guilds = all_guilds)
async def self(interaction: discord.Interaction, role: str):
    await interaction.response.send_message("Przeszukuję użytkowników, proszę czekać", ephemeral=True)
    try:
        if "<@&" in role:
            roles = [int(rola[3:-1]) for rola in role.split()]
        else:
            roles = [utils.get(interaction.guild.roles, name = rola.replace("@", "")).id for rola in role.split()]

        users = ""
        for user in interaction.guild.members:
            for rola in roles:
                rola = interaction.guild.get_role(rola)
                if rola not in user.roles:
                    break
            else:
                users += user.mention + "\n"
            
        if users == "":
            txt = "Nie znaleziono użytkownika, który ma wszystkie te role:"
            for rola in roles:
                txt += f" <@&{rola}>"
        else:
            txt = "Użytkownicy z rolami:"
            for rola in roles:
                txt += f" <@&{rola}>"
            txt += "\n" + users

        await asyncio.sleep(5)

        #await interaction.edit_original_response(content = interaction.user.mention + txt)
        await interaction.delete_original_response()
        await interaction.followup.send(interaction.user.mention + ", " + txt, ephemeral=True)
    except:
        #await interaction.edit_original_response(content = f"{interaction.user.mention} coś poszło nie tak")
        await interaction.delete_original_response()
        await interaction.followup.send(f"{interaction.user.mention} coś poszło nie tak", ephemeral=True)

#keep_alive()

for x in range(2):
    try:
        client.run(TOKEN)
        break
    except:
        print("kill 1")
        os.system("kill 1")