from discord.ext import commands
from discord.utils import get
import discord
from dotenv import load_dotenv
import os
import random

load_dotenv()

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='/', intents=intents)

TOKEN = os.getenv('DISCORD_TOKEN')

BUILDINGS = ['test', 'cse1', 'cse2', 'ode']

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command(name='add-location',
                help=(f'Given a building code and room number, adds a new study location.\n'
                      f'Usage: `/add-location building number` where `building` is a building '
                      f'code and `number` is the room number.'),
                brief='Adds a new study location')
async def add_location(ctx, building, number):
  # validate building and number
  building = building.lower()
  if building not in BUILDINGS:
    await ctx.channel.send(f'Building \"{building}\" not supported. Please try one of '
                           f'{BUILDINGS}!')
    return
  if not number.isnumeric():
    await add_location_error(ctx, None)
    return

  # check if the location channel exists already
  location = f'{building}-{number}'
  category = get(ctx.guild.categories, name='location-channels')
  channel = get(category.text_channels, name=location)
  if channel:
    await ctx.channel.send(f'Location \"{location}\" already exists. Please use the '
                           f'`/tag-location` command to tag yourself!')
    return

  # create the location channel and role if it does not already exist
  overwrites = {
    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
    ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
  }
  channel = await ctx.guild.create_text_channel(f'{location}', overwrites=overwrites,
                                                category=category)
  role = await ctx.guild.create_role(name=location, colour=random.randint(0, 0xFFFFFF), hoist=True)
  await channel.set_permissions(role, read_messages=True, send_messages=True)
  await ctx.author.add_roles(role, reason='/tag-location command')

  await ctx.channel.send(f'Location {location} added!')
  await channel.send(f'Welcome <@{ctx.author.id}>!')


@add_location.error
async def add_location_error(ctx, error):
  await ctx.channel.send(f'Usage: `/add-location building number` where `building` is a building '
                         f'code and `number` is the room number.')


@client.command(name='tag-location',
                help=(f'Given a building code and room number, gives you the role for that '
                      f'location,\n'
                      f'Usage: `/tag-location building number` where `building` is a building '
                      f'code and `number` is the room number.'),
                brief='Gives you the role for a location')
async def tag_location(ctx, building, number):
  # validate building and number
  location = f'{building.lower()}-{number}'
  category = get(ctx.guild.categories, name='location-channels')
  channel = get(category.text_channels, name=location)
  if not channel:
    await ctx.channel.send(f'Location \"{location}\" does not exist. Please use the '
                           f'`/add-location` command to add that location.')

  # Check if user already has the role
  role = get(ctx.guild.roles, name=location)
  if role in ctx.author.roles:
    await ctx.channel.send(f'You already have the role for {location}!')
    return

  # Give the location role to the user
  await ctx.author.add_roles(role, reason='/tag-location command')
  await ctx.channel.send(f'Location role for {location} added!')
  await channel.send(f'Welcome <@{ctx.author.id}>!')


@tag_location.error
async def tag_location_error(ctx, error):
  await ctx.channel.send(f'Usage: `/tag-location building number` where `building` is a building '
                         f'code and `number` is the room number.')

client.run(TOKEN)