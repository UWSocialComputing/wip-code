from discord.ext import commands
import discord
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='/', intents=intents)

TOKEN = os.getenv('DISCORD_TOKEN')

BUILDINGS = ['cse1', 'cse2', 'ode']
LOCATIONS = {}

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command(name='add-location',
                help='Given a building code and room number, adds a new study location. e.g. `/add-location` CSE2 114',
                brief='Adds a new study location')
async def add_location(ctx, building, room_no):
  location = f'{building.lower()}-{room_no}'
  if location in LOCATIONS:
    await ctx.channel.send(f'Location {location} already exists. Please use the `tag-location` command to tag yourself!')
    return
  else:
    overwrites = {
      ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
      ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
    }
    channel = await ctx.guild.create_text_channel(f'{location}', overwrites=overwrites)
    LOCATIONS[location] = channel
    await ctx.channel.send(f'Location {location} added!')

client.run(TOKEN)