import discord
from discord import app_commands, ui
from discord.ui import View

import pytz
import datetime
import json


with open("./token.json") as file:
    TOKEN = json.load(file)["queue"]


class aClient(discord.Client):

    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False
        self.added = False

        self.dluga = {}
        self.kolejka = []
        self.krotka = {}



        # można edytować

        self.timezone = pytz.timezone("Europe/Warsaw") # strefa czasowa

        # emotki do przycisków
        self.dluga_img = "🍗"
        self.krotka_img = "🍩"
        self.kolejka_img = "📝"
        self.wroc_img = "✅"

        self.max = 2 # maksymalna ilość osób na długiej przerwie

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced: # włączenie komend /
            await tree.sync()
            self.synced = True

        if not self.added: # włączenei wiadomości embed
            self.add_view(Break_Ticket())
            self.added = True

        self.przerwa_kanal = self.get_channel(1198967363937255486) # kanał z wysłaną wiadomością embed
        self.przerwa_msg = await self.przerwa_kanal.fetch_message(1202616005029924885) # wysłana wiadomość embed

        print("Bot jest gotowy")

    async def update_embed(self):
        dluga = ""
        kolejka = ""
        krotka = ""
        x = 1
        for key in self.dluga:
            dluga += f"{x}. {key} | od `{self.dluga[key]}`\n"
            x += 1

        x = 1
        for key in self.krotka:
            krotka += f"{x}. {key} | od `{self.krotka[key]}`\n"
            x += 1

        x = 1
        for member in self.kolejka:
            kolejka += f"{x}. {member.mention}\n"
            x += 1

        embed = discord.Embed(
            title = "Przerwy CeZ",
            description = f"Kliknij prycisk by zapisać się do kolejki {self.kolejka_img} na długą przerwę, lub jeśli idziesz na krótką {self.krotka_img} lub długą {self.dluga_img} przerwę.\nNie zapomnij kliknąć wróciłem/am {self.wroc_img} po powrocie",
            color = discord.Colour.from_str("#02f5f5")
        )
        embed.add_field(name = "Na długiej przerwie", value = dluga, inline = True)
        embed.add_field(name = "Na krótkiej przerwie", value = krotka, inline = True)
        embed.add_field(name = "Kolejka na długą przerwę", value = kolejka, inline = False)
        embed.set_footer(text = "Created by Filip Mickiewicz")

        await self.przerwa_msg.edit(embed = embed)

    def get_time(self):
        return datetime.datetime.now(tz = self.timezone).strftime("%H:%M")
    
    async def next_break(self):
        if len(self.kolejka) > 0:
            member = self.kolejka[0]

            embed = discord.Embed(
                title = "Przerwy CeZ",
                description = "Twoja kolej na długą przerwę",
                color = discord.Colour.from_str("#02f5f5")
            )
            await member.send(embed = embed, view = Priv_Btn())


client = aClient()
tree = app_commands.CommandTree(client)


class Priv_Btn(View):
    def __init__(self) -> None:
        super().__init__()
    
    @ui.button(label = "Idę", emoji = f"{client.dluga_img}")
    async def kolejka_btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(thinking = True)

        client.dluga[interaction.user.mention] = client.get_time()
        client.kolejka.remove(interaction.user)

        await client.update_embed()

        embed = discord.Embed(
            title = "Przerwy CeZ",
            description = "Miłej zabawy 😀",
            color = discord.Colour.from_str("#02f5f5")
        )
        await interaction.message.delete()
        await interaction.edit_original_response(embed = embed)

    @ui.button(label = "Rezygnuję", emoji = "❌")
    async def dluga_btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(thinking = True)
        
        client.kolejka.remove(interaction.user)
        await client.update_embed()

        embed = discord.Embed(
            title = "Przerwy CeZ",
            description = f"Jeśli chcesz skorzystać z przerwy zapisz się jeszcze raz do kolejki {client.przerwa_kanal.mention}",
            color = discord.Colour.from_str("#02f5f5")
        )
        await interaction.message.delete()
        await interaction.edit_original_response(embed = embed)

        await client.next_break()

class Break_Ticket(View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @ui.button(label = "Kolejka", emoji = f"{client.kolejka_img}", custom_id = "kolejka_btn")
    async def kolejka_btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(thinking = True, ephemeral = True)

        if interaction.user.mention in client.kolejka:
            await interaction.edit_original_response(content = "Już jesteś w kolejce na długą przerwę")
        else:
            client.kolejka.append(interaction.user)

            await client.update_embed()

            if len(client.kolejka) == 1 and len(client.dluga) == 0:
                await interaction.edit_original_response(content = f"Nie ma nikogo w kolejce, możesz iść od razu. Nie zapomnij kliknąć `Długa` {client.dluga_img}")
            else:
                await interaction.edit_original_response(content = "Dodano cię do kolejki")

    @ui.button(label = "Długa", emoji = f"{client.dluga_img}", custom_id = "dluga_btn")
    async def dluga_btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(thinking = True, ephemeral = True)

        if interaction.user.mention in client.dluga or interaction.user.mention in client.krotka:
            await interaction.edit_original_response(content = "Już jesteś na przerwie")
        elif interaction.user in client.kolejka or len(client.kolejka) == 0:
            client.dluga[interaction.user.mention] = client.get_time()
            if interaction.user in client.kolejka:
                client.kolejka.remove(interaction.user)

            await client.update_embed()
            await interaction.edit_original_response(content = f"Możesz iść na długą {client.dluga_img} przerwę")
        else:
            await interaction.edit_original_response(content = f"Nie zapisałeś się na przerwę, by to zrobić kliknij `Kolejka` {client.kolejka_img}")

    @ui.button(label = "Krótka", emoji = f"{client.krotka_img}", custom_id = "krotka_btn")
    async def krotka_btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(thinking = True, ephemeral = True)

        if interaction.user.mention in client.dluga or interaction.user.mention in client.krotka:
            await interaction.edit_original_response(content = "Jesteś już na przerwie")
        else:
            client.krotka[interaction.user.mention] = client.get_time()

            await client.update_embed()
            await interaction.edit_original_response(content = f"Możesz iść na krótką {client.krotka_img} przerwę")

    @ui.button(label = "Wróciłem/am", emoji = f"{client.wroc_img}", custom_id = "wroc_btn")
    async def wroc_btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(thinking = True, ephemeral = True)

        if interaction.user.mention in client.dluga:
            del client.dluga[interaction.user.mention]
            
            await client.update_embed()
            await interaction.edit_original_response(content = "Możesz zacząć pracować 😀")

            await client.next_break()
        elif interaction.user.mention in client.krotka:
            del client.krotka[interaction.user.mention]
                
            await client.update_embed()
            await interaction.edit_original_response(content = "Możesz zacząć pracować 😀")
        else:
            await interaction.edit_original_response(content = "Nie jesteś aktualnie na przerwie")


@tree.command(name = 'przerwy', description = 'Wysyła wiadomość do zarządzania przerwami')
async def self(interaction: discord.Interaction):
    if client.przerwa_msg == "":
        embed = discord.Embed(
            title = "Przerwy CeZ",
            description = f"Kliknij prycisk by zapisać się do kolejki {client.kolejka_img} na długą przerwę, lub jeśli idziesz na krótką {client.krotka_img} lub długą {client.dluga_img} przerwę.\nNie zapomnij kliknąć wróciłem/am {client.wroc_img} po powrocie",
            color = discord.Colour.from_str("#02f5f5")
        )
        embed.add_field(name = "Na długiej przerwie", value = "", inline = True)
        embed.add_field(name = "Na krótkiej przerwie", value = "", inline = True)
        embed.add_field(name = "Kolejka na długą przerwę", value = "", inline = False)
        embed.set_footer(text = "Created by Filip Mickiewicz")

        await interaction.channel.send(embed = embed, view = Break_Ticket())
        await interaction.response.send_message('Utworzono wiadomość', ephemeral = True)
    else:
        await interaction.response.send_message('Wiadomość już istnieje', ephemeral = True)


client.run(TOKEN)