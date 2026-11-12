import discord
from discord.ext import commands
from discord import app_commands
import os, aiohttp

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")

async def get_roblox_avatar(nome_roblox):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [nome_roblox], "excludeBannedUsers": False}) as r:
                data = await r.json()
                if not data.get("data"):
                    return nome_roblox, None
                user_id = data["data"][0]["id"]
                username = data["data"][0]["name"]
            async with s.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png&isCircular=false") as r2:
                data2 = await r2.json()
                return username, data2["data"][0]["imageUrl"]
    except:
        return nome_roblox, None

async def trova_log(guild):
    for nome in ["cc", "log-moderazione", "ban-e-warn", "log-warn", "log-ban"]:
        ch = discord.utils.get(guild.channels, name=nome)
        if ch:
            return ch
    return None

class ModModal(discord.ui.Modal):
    def __init__(self, tipo):
        super().__init__(title=f"{tipo} - Emeralds RP")
        self.tipo = tipo
        self.add_item(discord.ui.TextInput(label="Nome giocatore Roblox", placeholder="Es: Gigitopo17", required=True, max_length=50))
        self.add_item(discord.ui.TextInput(label="Motivazione", placeholder="Es: Cheat / Insulti", required=True, style=discord.TextStyle.paragraph, max_length=500))
        self.add_item(discord.ui.TextInput(label="Vittima (se c'e')", placeholder="Nome o Nessuna", required=False, max_length=50))
    async def on_submit(self, interaction: discord.Interaction):
        nome_roblox = self.children[0].value
        motivo = self.children[1].value
        vittima = self.children[2].value or "Nessuna"
        await interaction.response.send_message(f"⏳ Sto inviando {self.tipo} per **{nome_roblox}**...", ephemeral=True)
        username, avatar = await get_roblox_avatar(nome_roblox)
        log = await trova_log(interaction.guild) or interaction.channel
        colore = 0xff0000 if self.tipo == "BAN" else 0xffa500
        emoji = "🔨" if self.tipo == "BAN" else "⚠️"
        embed = discord.Embed(title=f"{emoji} {self.tipo} - EMERALDS RP", color=colore)
        if avatar:
            embed.set_thumbnail(url=avatar)
        embed.add_field(name="🎮 Giocatore Roblox", value=f"**{username}**", inline=True)
        embed.add_field(name="👮 Operatore", value=interaction.user.mention, inline=True)
        embed.add_field(name="👤 Vittima", value=vittima, inline=True)
        embed.add_field(name="📝 Motivazione", value=motivo, inline=False)
        await log.send(embed=embed)
        await interaction.followup.send(f"✅ {self.tipo} inviato in {log.mention}!", ephemeral=True)

class ModView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="⚠️ WARN", style=discord.ButtonStyle.primary, custom_id="warn_btn_v3")
    async def warn_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ModModal("WARN"))
    @discord.ui.button(label="🔨 BAN", style=discord.ButtonStyle.red, custom_id="ban_btn_v3")
    async def ban_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ModModal("BAN"))

class TurniView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🟢 Entra in servizio", style=discord.ButtonStyle.green, custom_id="entra_v3")
    async def entra(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"✅ {interaction.user.mention} è entrato in servizio!")
    @discord.ui.button(label="🔴 Fuori servizio", style=discord.ButtonStyle.red, custom_id="esci_v3")
    async def esci(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"🔴 {interaction.user.mention} è uscito dal servizio!")

@bot.tree.command(name="pannello_moderazione", description="Pannello BAN / WARN Emeralds RP")
async def pannello_mod(interaction: discord.Interaction):
    embed = discord.Embed(title="🛡️ PANNELLO MODERAZIONE - EMERALDS RP", description="Clicca un bottone per aprire il form.", color=0xff0000)
    await interaction.response.send_message(embed=embed, view=ModView())

@bot.tree.command(name="pannello", description="Pannello turni Emeralds RP")
async def pannello(interaction: discord.Interaction):
    embed = discord.Embed(title="EMERALDS RP · Turni staff", description="Usa i bottoni per entrare / uscire dal servizio.", color=0x00ff00)
    await interaction.response.send_message(embed=embed, view=TurniView())

@bot.event
async def on_ready():
    bot.add_view(ModView())
    bot.add_view(TurniView())
    try:
        synced = await bot.tree.sync()
        print(f"Syncati {len(synced)} comandi slash!")
    except Exception as e:
        print(f"Errore sync: {e}")
    print(f"Online come {bot.user} - V3 SLASH PRONTO!")

bot.run(TOKEN)
