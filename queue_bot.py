# pip install discord.py pytz

import discord
from discord import app_commands, ui
from discord.ui import View
from discord.ext import tasks

import pytz
import datetime
import json
import os

try:
   os.mkdir("./backup")
except:
    print("Folder istnieje")


# Discord bot TOKEN
try:
    with open("./token.json") as file:
        TOKEN = json.load(file)["queue"]
except:
    TOKEN = None


class aClient(discord.Client):
    
  def __init__(self):
    super().__init__(intents=discord.Intents.all())
    self.synced = False
    self.added = False
    self.looped = False
    self.backup = False

    self.dluga = {}
    self.kolejka = []
    self.krotka = {}

    self.author = "Created by Filip Mickiewicz | mirrovex@wp.pl"
    self.author_img = "https://avatars.githubusercontent.com/u/69217021?v=4"
    self.author_id = 1193838417851727892

    # ===== MOŻNA EDYTOWAĆ ===== #

    self.timezone = pytz.timezone("Europe/Warsaw")  # strefa czasowa

    # emotki do przycisków
    self.dluga_img = "🍗"
    self.krotka_img = "☕"
    self.kolejka_img = "📝"
    self.wroc_img = "✅"

    self.max = 2  # maksymalna ilość osób na długiej przerwie
    self.admin_role = "1019214716356272128"  # id roli, która może używać /kopiuj /wklej i /usuń

    self.opis = f"`Kolejka` {self.kolejka_img} - Zapis do kolejki. Kliknij ponownie by się wypisać\n`Długa` {self.dluga_img} - Przerwa wymagająca kolejki\n`Szybka` {self.krotka_img} - Przerwa niewymagająca kolejki\n`Wróciłem/am` {self.wroc_img} - Powrót z dowolnej przerwy. Po powrocie z długiej przerwy automatycznie zostanie wysłana wiadomość prywatna do następnej osoby z kolejki"
    #self.opis = f"Kliknij przycisk by zapisać się do kolejki {self.kolejka_img} na długą przerwę, lub jeśli idziesz na szybką {self.krotka_img} lub długą {self.dluga_img} przerwę.\nNie zapomnij kliknąć wróciłem/am {self.wroc_img} po powrocie"

    # ===== MOŻNA EDYTOWAĆ ===== #

  async def on_ready(self):
    await self.wait_until_ready()
    if not self.synced:  # włączenie komend /
      await tree.sync()
      self.synced = True

    if not self.added:  # włączeie wiadomości embed
      self.add_view(Break_Ticket())
      self.added = True

    if not self.looped:
      backup_loop.start()
      self.looped = True

    try:
      with open("./backup/przerwa_msg.json", "r") as file:
        json_object = json.load(file)

      self.przerwa_kanal = self.get_channel(json_object["channel_id"])
      self.przerwa_msg = await self.przerwa_kanal.fetch_message(
          json_object["msg_id"])
    except:
      self.przerwa_kanal = None
      self.przerwa_msg = None

    if self.max > 1:
      opis = self.opis + f"\n\nNa przerwę można chodzić po **{self.max}** osoby (jeśli jest powyżej 15 zalogowanych i brak kolejek)"
    else:
      opis = self.opis + f"\n\nNa przerwę można chodzić po **{self.max}** osobę"

    embed = discord.Embed(title="Przerwy CeZ",
                          description=opis,
                          color=discord.Colour.from_str("#02f5f5"))
    embed.add_field(name="Na długiej przerwie", value="", inline=True)
    embed.add_field(name="Na szybkiej przerwie", value="", inline=True)
    embed.add_field(name="Kolejka na długą przerwę", value="", inline=False)
    embed.set_footer(text=self.author, icon_url=self.author_img)

    await self.przerwa_msg.edit(embed=embed, view=Break_Ticket())

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
      kolejka += f"{x}. <@{member}>\n"
      x += 1

    if self.max > 1:
      opis = self.opis + f"\n\nNa przerwę można chodzić po **{self.max}** osoby (jeśli jest powyżej 15 zalogowanych i brak kolejek)"
    else:
      opis = self.opis + f"\n\nNa przerwę można chodzić po **{self.max}** osobę"

    embed = discord.Embed(title="Przerwy CeZ",
                          description=opis,
                          color=discord.Colour.from_str("#02f5f5"))
    embed.add_field(name="Na długiej przerwie", value=dluga, inline=True)
    embed.add_field(name="Na szybkiej przerwie", value=krotka, inline=True)
    embed.add_field(name="Kolejka na długą przerwę",
                    value=kolejka,
                    inline=False)
    embed.set_footer(text=self.author, icon_url=self.author_img)

    await self.przerwa_msg.edit(embed=embed)

  def get_time(self):
    return datetime.datetime.now(tz=self.timezone).strftime("%H:%M")

  async def next_break(self, guild):
    if len(self.kolejka) > 0:
      member = guild.get_member(self.kolejka[0])

      embed = discord.Embed(title="Przerwy CeZ",
                            description="Twoja kolej na długą przerwę",
                            color=discord.Colour.from_str("#02f5f5"))
      await member.send(embed=embed, view=Priv_Btn(guild))


client = aClient()
tree = app_commands.CommandTree(client)


@tasks.loop(minutes=10)
async def backup_loop():
  if client.backup:
    with open("./backup/kolejka.json", "w") as file:
      json_object = json.dumps(client.kolejka)
      file.write(json_object)

    with open("./backup/dluga.json", "w") as file:
      json_object = json.dumps(client.dluga)
      file.write(json_object)

    with open("./backup/krotka.json", "w") as file:
      json_object = json.dumps(client.krotka)
      file.write(json_object)

    print("--- BACKUP ---")
  else:
    client.backup = True


class Anuluj_Btn(View):

  def __init__(self, msg) -> None:
    super().__init__()

    self.msg = msg

  @ui.button(label="Tak", emoji="✅")
  async def yes_btn(self, interaction: discord.Interaction, button: ui.Button):

    print("Tak |", interaction.user.id, interaction.user.name,
          interaction.user.nick)
    client.kolejka.remove(interaction.user.id)
    await client.update_embed()

    await self.msg.edit(content="Usunięto z kolejki", view=None)

  @ui.button(label="Anuluj", emoji="❌")
  async def no_btn(self, interaction: discord.Interaction, button: ui.Button):
    await self.msg.edit(content="Dalej jesteś w kolejce", view=None)


class Priv_Btn(View):

  def __init__(self, guild) -> None:
    super().__init__()
    self.guild = guild

  @ui.button(label="Idę", emoji=f"{client.dluga_img}")
  async def kolejka_btn(self, interaction: discord.Interaction,
                        button: ui.Button):
    await interaction.response.defer(thinking=True)

    print("Idę |", interaction.user.id, interaction.user.name,
          interaction.user.global_name)

    if interaction.user.id in client.kolejka:
      client.dluga[interaction.user.mention] = client.get_time()
      client.kolejka.remove(interaction.user.id)

      await client.update_embed()

    embed = discord.Embed(title="Przerwy CeZ",
                          description="Miłej zabawy 😀",
                          color=discord.Colour.from_str("#02f5f5"))
    await interaction.message.delete()
    await interaction.edit_original_response(embed=embed)

  @ui.button(label="Rezygnuję", emoji="❌")
  async def dluga_btn(self, interaction: discord.Interaction,
                      button: ui.Button):
    await interaction.response.defer(thinking=True)

    print("Rezygnuję |", interaction.user.id, interaction.user.name,
          interaction.user.global_name)

    if interaction.user.id in client.kolejka:
      client.kolejka.remove(interaction.user.id)
      await client.update_embed()

    embed = discord.Embed(
        title="Przerwy CeZ",
        description=
        f"Jeśli chcesz skorzystać z przerwy zapisz się jeszcze raz do kolejki {client.przerwa_kanal.mention}",
        color=discord.Colour.from_str("#02f5f5"))
    await interaction.message.delete()
    await interaction.edit_original_response(embed=embed)

    await client.next_break(self.guild)


class Break_Ticket(View):

  def __init__(self) -> None:
    super().__init__(timeout=None)

  @ui.button(label="Kolejka",
             emoji=f"{client.kolejka_img}",
             custom_id="kolejka_btn")
  async def kolejka_btn(self, interaction: discord.Interaction,
                        button: ui.Button):
    await interaction.response.defer(thinking=True, ephemeral=True)

    if interaction.user.id in client.kolejka:
      await interaction.edit_original_response(
          content="Już jesteś w kolejce na długą przerwę\nChcesz się wypisać?",
          view=Anuluj_Btn(await interaction.original_response()))
    else:
      client.kolejka.append(interaction.user.id)

      await client.update_embed()

      if len(client.kolejka) == 1 and len(client.dluga) == 0:
        await interaction.edit_original_response(
            content=
            f"Nie ma nikogo w kolejce, możesz iść od razu. Nie zapomnij kliknąć `Długa` {client.dluga_img}"
        )
      else:
        await interaction.edit_original_response(
            content="Dodano cię do kolejki")

  @ui.button(label="Długa", emoji=f"{client.dluga_img}", custom_id="dluga_btn")
  async def dluga_btn(self, interaction: discord.Interaction,
                      button: ui.Button):
    await interaction.response.defer(thinking=True, ephemeral=True)

    if interaction.user.mention in client.dluga or interaction.user.mention in client.krotka:
      await interaction.edit_original_response(content="Już jesteś na przerwie"
                                               )
    elif interaction.user.id in client.kolejka or len(client.kolejka) == 0:
      client.dluga[interaction.user.mention] = client.get_time()
      if interaction.user.id in client.kolejka:
        client.kolejka.remove(interaction.user.id)

      await client.update_embed()
      await interaction.edit_original_response(
          content=f"Możesz iść na długą {client.dluga_img} przerwę")
    else:
      await interaction.edit_original_response(
          content=
          f"Nie zapisałeś się na przerwę, by to zrobić kliknij `Kolejka` {client.kolejka_img}"
      )

  @ui.button(label="Szybka",
             emoji=f"{client.krotka_img}",
             custom_id="krotka_btn")
  async def krotka_btn(self, interaction: discord.Interaction,
                       button: ui.Button):
    await interaction.response.defer(thinking=True, ephemeral=True)

    if interaction.user.mention in client.dluga or interaction.user.mention in client.krotka:
      await interaction.edit_original_response(content="Jesteś już na przerwie"
                                               )
    else:
      client.krotka[interaction.user.mention] = client.get_time()

      await client.update_embed()
      await interaction.edit_original_response(
          content=f"Możesz iść na szybką {client.krotka_img} przerwę")

  @ui.button(label="Wróciłem/am",
             emoji=f"{client.wroc_img}",
             custom_id="wroc_btn")
  async def wroc_btn(self, interaction: discord.Interaction,
                     button: ui.Button):
    await interaction.response.defer(thinking=True, ephemeral=True)

    if interaction.user.mention in client.dluga:
      del client.dluga[interaction.user.mention]

      await client.update_embed()
      await interaction.edit_original_response(
          content="Możesz zacząć pracować 😀")

      await client.next_break(interaction.guild)
    elif interaction.user.mention in client.krotka:
      del client.krotka[interaction.user.mention]

      await client.update_embed()
      await interaction.edit_original_response(
          content="Możesz zacząć pracować 😀")
    else:
      await interaction.edit_original_response(
          content="Nie jesteś aktualnie na przerwie")


@tree.command(name='przerwy',
              description='Wysyła wiadomość do zarządzania przerwami')
async def self(interaction: discord.Interaction):
  if client.admin_role == None or client.admin_role in str(
      interaction.user.roles) or interaction.user.id == client.author_id:

    try:
      client.przerwa_msg = await client.przerwa_kanal.fetch_message(
          client.przerwa_msg.id)
    except:
      client.przerwa_msg = None

    if client.przerwa_msg == None:
      embed = discord.Embed(title="Przerwy CeZ",
                            description=client.opis,
                            color=discord.Colour.from_str("#02f5f5"))
      embed.add_field(name="Na długiej przerwie", value="", inline=True)
      embed.add_field(name="Na szybkiej przerwie", value="", inline=True)
      embed.add_field(name="Kolejka na długą przerwę", value="", inline=False)
      embed.set_footer(text=client.author, icon_url=client.author_img)

      msg = await interaction.channel.send(embed=embed, view=Break_Ticket())
      msg_channel = {"msg_id": msg.id, "channel_id": msg.channel.id}
      client.przerwa_msg = msg

      with open("./backup/przerwa_msg.json", "w") as file:
        json_object = json.dumps(msg_channel, indent=2)
        file.write(json_object)

      await interaction.response.send_message('Utworzono wiadomość',
                                              ephemeral=True)
    else:
      await interaction.response.send_message('Wiadomość już istnieje',
                                              ephemeral=True)
  else:
    await interaction.response.send_message("Nie masz do tego uprawnień",
                                            ephemeral=True)


@tree.command(name='kopiuj', description='Kopiuje zapisane osoby')
async def self(interaction: discord.Interaction):
  if client.admin_role == None or client.admin_role in str(
      interaction.user.roles) or interaction.user.id == client.author_id:
    await interaction.response.defer(thinking=True, ephemeral=True)

    with open("./backup/kolejka.json", "w") as file:
      json_object = json.dumps(client.kolejka)
      file.write(json_object)

    with open("./backup/dluga.json", "w") as file:
      json_object = json.dumps(client.dluga)
      file.write(json_object)

    with open("./backup/krotka.json", "w") as file:
      json_object = json.dumps(client.krotka)
      file.write(json_object)

    await interaction.edit_original_response(content="Skopiowano osoby")
  else:
    await interaction.response.send_message("Nie masz do tego uprawnień",
                                            ephemeral=True)


@tree.command(name='wklej', description='Wkleja skopiowane osoby')
async def self(interaction: discord.Interaction):
  if client.admin_role == None or client.admin_role in str(
      interaction.user.roles) or interaction.user.id == client.author_id:
    await interaction.response.defer(thinking=True, ephemeral=True)

    with open("./backup/kolejka.json", "r") as file:
      json_object = json.load(file)
      client.kolejka = json_object

    with open("./backup/dluga.json", "r") as file:
      json_object = json.load(file)
      client.dluga = json_object

    with open("./backup/krotka.json", "r") as file:
      json_object = json.load(file)
      client.krotka = json_object

    await client.update_embed()

    await interaction.edit_original_response(content="Wklejono osoby")
  else:
    await interaction.response.send_message("Nie masz do tego uprawnień",
                                            ephemeral=True)


@tree.command(name='wyczyść', description='Usuwa wszystkie osoby')
async def self(interaction: discord.Interaction):
  if client.admin_role == None or client.admin_role in str(
      interaction.user.roles) or interaction.user.id == client.author_id:
    await interaction.response.defer(thinking=True, ephemeral=True)

    client.kolejka = []
    client.dluga = {}
    client.krotka = {}

    await client.update_embed()

    await interaction.edit_original_response(content="Usunięto osoby")
  else:
    await interaction.response.send_message("Nie masz do tego uprawnień",
                                            ephemeral=True)


del_type = [
    app_commands.Choice(name="Długa", value="dluga"),
    app_commands.Choice(name="Szybka", value="szybka"),
    app_commands.Choice(name="Kolejka", value="kolejka")
]


@app_commands.choices(rodzaj=del_type)
@tree.command(name='usuń', description='Usuwa wiadomość')
async def self(interaction: discord.Interaction,
               osoba: discord.Member,
               rodzaj: str = "wszystko"):
  if client.admin_role == None or client.admin_role in str(
      interaction.user.roles) or interaction.user.id == client.author_id:

    if rodzaj == "dluga" or rodzaj == "wszystko":
      try:
        del client.dluga[osoba.mention]
      except:
        print("nie znaleziono użytkownika")
    if rodzaj == "szybka" or rodzaj == "wszystko":
      try:
        del client.krotka[osoba.mention]
      except:
        print("nie znaleziono użytkownika")
    if rodzaj == "kolejka" or rodzaj == "wszystko":
      try:
        client.kolejka.remove(osoba.id)
      except:
        print("nie znaleziono użytkownika")

    await client.update_embed()

    await interaction.response.send_message("Usunięto użytkownika",
                                            ephemeral=True)

  else:
    await interaction.response.send_message("Nie masz do tego uprawnień",
                                            ephemeral=True)


"""@tree.command(name='usuń', description='Usuwa wiadomość')
async def self(interaction: discord.Interaction, msg_id: str):
  if client.admin_role == None or client.admin_role in str(
      interaction.user.roles):
    msg = await interaction.channel.fetch_message(int(msg_id))
    await msg.delete()
    await interaction.response.send_message("Usunięto wiadomość",
                                            ephemeral=True)

  else:
    await interaction.response.send_message("Nie masz do tego uprawnień",
                                            ephemeral=True)"""


@tree.command(name='kolejka', description='Zarządzanie kolejnością w kolejce')
async def self(interaction: discord.Interaction, osoby: str):
  if client.admin_role == None or client.admin_role in str(
      interaction.user.roles) or interaction.user.id == client.author_id:
    await interaction.response.defer(thinking=True, ephemeral=True)

    kolejka = [
        int(
            id.replace("<", "").replace("@", "").replace("!",
                                                         "").replace(">", ""))
        for id in osoby.split()
    ]
    client.kolejka = kolejka
    await client.update_embed()

    await interaction.edit_original_response(content="Zaktualizowano kolejność"
                                             )

  else:
    await interaction.response.send_message("Nie masz do tego uprawnień",
                                            ephemeral=True)


@tree.command(name='max',
              description='Ustawianie po ile osób można chodzić na przerwę')
async def self(interaction: discord.Interaction, max_liczba: int):
  if client.admin_role == None or client.admin_role in str(
      interaction.user.roles) or interaction.user.id == client.author_id:
    await interaction.response.defer(thinking=True, ephemeral=True)

    client.max = max_liczba
    await client.update_embed()

    await interaction.edit_original_response(
        content="Zaktualizowano liczbę osób na przerwie")

  else:
    await interaction.response.send_message("Nie masz do tego uprawnień",
                                            ephemeral=True)


client.run(TOKEN)
