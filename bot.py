import discord
from discord.ext import commands, tasks
import datetime
import os

TOKEN = os.environ.get("TOKEN")
EXPLOIT_CHANNEL_ID = int(os.environ.get("EXPLOIT_CHANNEL_ID"))
OWNER_ID = int(os.environ.get("OWNER_ID"))
HEURE_ENVOI = 20

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté : {bot.user}")
    recap_hebdo.start()

@tasks.loop(hours=24)
async def recap_hebdo():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    if now.weekday() != 6 or now.hour != HEURE_ENVOI:
        return
    channel = bot.get_channel(EXPLOIT_CHANNEL_ID)
    if not channel:
        print("❌ Salon introuvable")
        return
    since = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    messages = []
    async for msg in channel.history(after=since, oldest_first=True):
        if not msg.author.bot and msg.content.strip():
            messages.append(msg)
    if not messages:
        contenu = "📜 **RÉCAP EXPLOITS**\n\nAucun exploit cette semaine."
    else:
        lignes = []
        for msg in messages:
            date = (msg.created_at + datetime.timedelta(hours=2)).strftime("%d/%m à %Hh%M")
            lignes.append(f"**{date}** — {msg.author.display_name}\n{msg.content}")
        debut = (since + datetime.timedelta(hours=2)).strftime("%d/%m")
        fin = now.strftime("%d/%m")
        contenu = f"📜 **RÉCAP EXPLOITS — Semaine du {debut} au {fin}**\n"
        contenu += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        contenu += "\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n".join(lignes)
        contenu += "\n\n━━━━━━━━━━━━━━━━━━━━━━"
    owner = await bot.fetch_user(OWNER_ID)
    if owner:
        if len(contenu) <= 1900:
            await owner.send(contenu)
        else:
            parties = []
            current = ""
            for ligne in contenu.split("\n"):
                if len(current) + len(ligne) + 1 > 1900:
                    parties.append(current)
                    current = ligne
                else:
                    current += "\n" + ligne
            if current:
                parties.append(current)
            for partie in parties:
                await owner.send(partie)
        print(f"✅ Récap envoyé à {owner.name}")

@recap_hebdo.before_loop
async def before_recap():
    await bot.wait_until_ready()

@bot.command(name="recap")
async def recap_manuel(ctx):
    if ctx.author.id != OWNER_ID:
        return
    await ctx.send("⏳ Génération du récap en cours...")
    channel = bot.get_channel(EXPLOIT_CHANNEL_ID)
    since = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    messages = []
    async for msg in channel.history(after=since, oldest_first=True):
        if not msg.author.bot and msg.content.strip():
            messages.append(msg)
    if not messages:
        await ctx.author.send("📜 **RÉCAP EXPLOITS**\n\nAucun exploit cette semaine.")
        return
    lignes = []
    for msg in messages:
        date = (msg.created_at + datetime.timedelta(hours=2)).strftime("%d/%m à %Hh%M")
        lignes.append(f"**{date}** — {msg.author.display_name}\n{msg.content}")
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    debut = (since + datetime.timedelta(hours=2)).strftime("%d/%m")
    fin = now.strftime("%d/%m")
    contenu = f"📜 **RÉCAP EXPLOITS — Semaine du {debut} au {fin}**\n"
    contenu += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    contenu += "\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n".join(lignes)
    contenu += "\n\n━━━━━━━━━━━━━━━━━━━━━━"
    if len(contenu) <= 1900:
        await ctx.author.send(contenu)
    else:
        parties = []
        current = ""
        for ligne in contenu.split("\n"):
            if len(current) + len(ligne) + 1 > 1900:
                parties.append(current)
                current = ligne
            else:
                current += "\n" + ligne
        if current:
            parties.append(current)
        for partie in parties:
            await ctx.author.send(partie)
    await ctx.send("✅ Récap envoyé en MP !")

bot.run(TOKEN)
