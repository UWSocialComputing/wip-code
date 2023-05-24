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

STUDY_LOCATIONS = {'test 123': [3, 4], 'cse1 111': [2, 4], 'cse2 20': [1, 1], 'ode 333': [5, 5]} # hardcoded data

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


@client.command(name='clear-role',
                 help='Removes a location role',
                 brief='Removes a location role')
async def clear_role(ctx, building, number):
  print(building)
  print(number)
  location = f'{building.lower()}-{number}'
  category = get(ctx.guild.categories, name='location-channels')
  channel = get(category.text_channels, name=location)
  if not channel:
    await ctx.channel.send(f'Location \"{location}\" does not exist. Please use the '
                           f'`/add-location` command to add that location.')
  
  # Check if user has the role
  role = get(ctx.guild.roles, name=location)
  if role not in ctx.author.roles:
    await ctx.channel.send(f'You do not have the role for {location}!')
    return
  
  # Remove the role from user
  await ctx.author.remove_roles(role, reason='/clear-role command')
  await ctx.channel.send(f'Location role for {location} removed!')
  await channel.send(f'{ctx.author.name} has left!')


@clear_role.error
async def clear_role_error(ctx, error):
  await ctx.channel.send('clear_role error`')


@client.command(name='list-info',
                help='Lists noise and busy-ness levels of all study locations',
                brief='Lists noise and busy-ness levels of all study locations')
async def list_info(ctx):
    info_table = '| Location | Noise | Busy-ness |\n' \
                 + '|----------|-------|-----------|\n'

    for location in STUDY_LOCATIONS:
        location_string = location
        location_length = len(location_string)
        noise_level = str(STUDY_LOCATIONS[location][0])
        busyness_level = str(STUDY_LOCATIONS[location][1])

        # Add padding to location string
        while location_length < 8:
            location_string += ' '
            location_length += 1

        info_table += ('| ' + location_string + ' |   ' + noise_level
                       + '   |     ' + busyness_level + '     |\n')

    await ctx.channel.send(f'Noise and Busy-ness Levels for each study location, '
                           f'on a scale of 1 (lowest) to 5 (highest)\n`{info_table}`')

    return

client.run(TOKEN)