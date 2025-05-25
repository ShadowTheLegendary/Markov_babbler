import json
import os
import re
import discord
from discord import app_commands
from discord.ext import commands
import Markov_babbler

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

TOKEN = os.getenv("MARKOV_TOKEN")
if not TOKEN:
    raise EnvironmentError("MARKOV_TOKEN environment variable not set")

bot = commands.Bot(command_prefix='/', intents=intents)

def get_guild_stats_path(guild_name):
    safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', guild_name)
    base_dir = "guild_data"
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, f"{safe_name}.json")

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} global command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.tree.command(name="babble", description="Generate Markov babble")
@app_commands.describe(sentences="Number of sentences to generate")
async def babble(interaction: discord.Interaction, sentences: int):
    try:
        path = get_guild_stats_path(interaction.guild.name)
        with open(path, 'r') as file:
            stats = json.load(file)
        output = Markov_babbler.babble(stats, sentences)
        await interaction.response.send_message(output)
    except FileNotFoundError:
        await interaction.response.send_message("Stats file not found.")
    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if not (message.content and not message.embeds and not message.attachments):
        return
    try:
        path = get_guild_stats_path(message.guild.name)
        try:
            with open(path, 'r') as file:
                message_stats = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            message_stats = {}
        message_stats = Markov_babbler.add_to_stats(message_stats, message.content)
        with open(path, 'w') as file:
            json.dump(message_stats, file, indent=4)
    except Exception as e:
        print(f"Error processing message: {e}")
    await bot.process_commands(message)

bot.run(TOKEN)
