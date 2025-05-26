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

def is_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.administrator

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    synced_total = 0
    try:
        for guild in bot.guilds:
            synced = await bot.tree.sync(guild=guild)
            print(f"Synced {len(synced)} command(s) to guild: {guild.name} (ID: {guild.id})")
            synced_total += len(synced)
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"Total commands synced: {synced_total}")

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

@app_commands.check(is_admin)
@bot.tree.command(name="remove", description="Remove a word from the training data")
@app_commands.describe(word="The word to remove")
async def remove(interaction: discord.Interaction, word: str):
    try:
        path = get_guild_stats_path(interaction.guild.name)
        with open(path, 'r') as file:
            content = file.read()
            message_stats = json.loads(content) if content else {}

        # Use message_stats for filtering
        stats = {k: [item for item in v if item != word] for k, v in message_stats.items() if k != word}

        with open(path, 'w') as file:
            json.dump(stats, file, indent=4)

        await interaction.response.send_message(f"Removed word '{word}' from training data.")

    except FileNotFoundError:
        await interaction.response.send_message("Stats file not found.")
    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}")

@app_commands.check(is_admin)
@bot.tree.command(name="clear", description="Clear the training data")
async def clear(interaction: discord.Interaction):
    stats = {}

    try:
        path = get_guild_stats_path(interaction.guild.name)
        with open(path, 'w') as file:
            json.dump(stats, file, indent=4)
        await interaction.response.send_message("Training data cleared.")
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
