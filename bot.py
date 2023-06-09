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
INFO_MSG = (':information_source: My name is WIP Bot, and I\'m here to help '
            'you find new study buddies and study locations!\n'
            ':arrow_forward: To get started, tag yourself at an existing '
            'location using the `tag-location` command or add a new location '
            'using the `add-location` command. Then, find your classmates!\n'
            ':question: Questions? Use the `/help` command to learn about '
            'all the commands!\n'
            ':tada: Happy studying!')
USAGE_MSGS = ['Usage: `/add-location building number` where `building` is a '
              'building name and `number` is a room number.',
              'Usage: `/tag-location building number` where `building` is a '
              'building name and `number` is a room number.',
              'Usage: `/leave building number` where `building` is a building '
              'name and `number` is a room number. Note that you must be '
              'holding the location role for this location.',
              'Usage: `/list-info`',
              'Usage: `update-noise building number value` where `building` '
              'a building name and `number` is a room number for a location '
              'that exists, and `value` is the current noise level (between 1 '
              'and 5, inclusive) of that location.',
              'Usage: `update-busy building number value` where `building` '
              'a building name and `number` is a room number for a location '
              'that exists, and `value` is the current \"busy-ness\" level '
              '(between 1 and 5, inclusive) of that location.',
              'Usage: `list-people building number` where `building` is a '
              'building name and `number` is a room number for a location '
              'exists',
              'Usage: `init`.']
BUILDINGS = ['cse1', 'cse2', 'ode']
# Note that these do not persist between bot instances, so don't restart the bot
# unless absolutely necessary!
USER_ROLE = {}
LOCATIONS = {}


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command(name='reset',
                help=('Resets WIP Bot for this server. Creates a new category '
                      'for location channels, overwriting any existing '
                      'location channels and deletes any building-related '
                      'roles.\n'
                      'ONLY FOR TESTING\n'
                      'Usage: `reset`.'),
                brief='Resets up WIP Bot for this server.',
                hidden=True)
async def reset(ctx):
  category = get(ctx.guild.categories, name='location-channels')
  if category:
    for channel in category.channels:
      await channel.delete()
    await category.delete()
  await ctx.guild.create_category('location-channels') 
  USER_ROLE.clear()
  LOCATIONS.clear()
  for role in ctx.guild.roles:
    if role.name.split()[0] in BUILDINGS:
      await role.delete()
  print('Reset complete!')

@reset.error
async def reset(ctx, error):
  '''
  FATAL ERROR: Terminates this instance of WIP Bot
  '''
  embed = discord.Embed(title=f':x: Something went wrong!',
                        description=('Please restart the bot and run `reset` '
                                     'again!'),
                        color=0xED4245)
  await ctx.channel.send(embed=embed)


@client.event
async def on_member_join(member):
  embed = discord.Embed(title=f'Welcome to {ctx.message.guild.name}!',
                        description=INFO_MSG,
                        color=0x57F287)
  await member.send(embed=embed)


@client.command(name='add-location',
                help=(f'Given a building code and room number, adds a new '
                      f'study location.\n'
                      f'{USAGE_MSGS[0].replace("`", "")}'),
                brief='Adds a new study location')
async def add_location(ctx, building, number):
  # validate building and number
  building = building.lower()
  if building not in BUILDINGS or not number.isnumeric():
    await add_location_error(ctx, None)
    return

  # check if the location channel exists already
  location = f'{building} {number}'
  channel_name = f'{building}-{number}'
  category = get(ctx.guild.categories, name='location-channels')
  channel = get(category.text_channels, name=channel_name)
  if channel:
    embed = discord.Embed(title=':x: Something went wrong!',
                          description=f'Location \"{location}\" already '
                                       'exists. Please use the `/tag-location` '
                                       'command to tag yourself!',
                          color=0xED4245)
    await ctx.channel.send(embed=embed)
    return

  # create the location channel and role if it does not already exist
  overwrites = {
    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
    ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
  }
  channel = await ctx.guild.create_text_channel(f'{channel_name}', 
                                                overwrites=overwrites,
                                                category=category)
  role = await ctx.guild.create_role(name=location, 
                                     colour=random.randint(0, 0xFFFFFF),
                                     hoist=True)
  await channel.set_permissions(role, read_messages=True, send_messages=True)
  LOCATIONS[location] = ['X', 'X']

  # remove the user's old location role, if one exists
  # then, give the role of the given location to the user
  user = ctx.author.id
  description = ':tada: Happy studying!'
  if user in USER_ROLE:
    args = USER_ROLE[user].split()
    await leave(ctx, args[0], args[1])
    description = f'Old location role for {args[0]} {args[1]} removed.\n' +\
                  description
  await ctx.author.add_roles(role, reason='/add-location command')
  USER_ROLE[user] = location

  # Confirm the successful addition of a new location and welcome the user at
  # the new location
  embed = discord.Embed(title=f':white_check_mark: Location {location} added!',
                        description=description,
                        color=0x57F287)
  await ctx.channel.send(embed=embed)
  await channel.send(f'Welcome <@{ctx.author.id}>!')


@add_location.error
async def add_location_error(ctx, error):
  info = '`building` must be one of the following: ```\n'
  for b in BUILDINGS:
    info += f'{b}\n'
  info += '```'
  embed = discord.Embed(title=f':x: Something went wrong!',
                        description=f'{USAGE_MSGS[0]}\n{info}',
                        color=0xED4245)
  await ctx.channel.send(embed=embed)


@client.command(name='tag-location',
                help=(f'Given a building code and room number, gives you the '
                      f'role for that location,\n'
                      f'{USAGE_MSGS[1].replace("`", "")}'),
                brief='Gives you the role for a location')
async def tag_location(ctx, building, number):
  # validate building and number
  location = f'{building.lower()} {number}'
  channel_name = f'{building.lower()}-{number}'
  category = get(ctx.guild.categories, name='location-channels')
  channel = get(category.text_channels, name=channel_name)
  if not channel:
    await tag_location_error(ctx, None)
    return

  # Check if user already has the role
  role = get(ctx.guild.roles, name=location)
  if role in ctx.author.roles:
    message = 'You already have the role for that location!'
    embed = discord.Embed(title=':x: Something went wrong!',
                          description=message,
                          color=0xED4245)
    await ctx.channel.send(embed=embed)
    return

  # remove the user's old location role, if one exists
  # then, give the role of the given location to the user
  user = ctx.author.id
  description = ':tada: Happy studying!'
  if user in USER_ROLE:
    args = USER_ROLE[user].split()
    await leave(ctx, args[0], args[1])
    description = f'Old location role for {args[0]} {args[1]} removed.\n' +\
                  description
  await ctx.author.add_roles(role, reason='/add-location command')
  USER_ROLE[user] = location

  # Confirm the successful addition of a new location and welcome the user at
  # the new location
  embed = discord.Embed(title=(f':white_check_mark: Location role for '
                               f'{location} added!'),
                        description=description,
                        color=0x57F287)
  await ctx.channel.send(embed=embed)
  await channel.send(f'Welcome <@{ctx.author.id}>!')


@tag_location.error
async def tag_location_error(ctx, error):
  info = 'Try tagging yourself at one of the following locations!```\n'
  for location in LOCATIONS.keys():
    info += f'{location}\n'
  info += '```'
  embed = discord.Embed(title=f':x: Something went wrong!',
                        description=f'{USAGE_MSGS[1]}\n{info}',
                        color=0xED4245)
  await ctx.channel.send(embed=embed)


@client.command(name='leave',
                 help=f'Leaves a location, removing the location role for the '
                      f'location you are currently at.\n'
                      f'{USAGE_MSGS[2].replace("`", "")}',
                 brief='Removes the location role you currently hold')
async def leave(ctx, building, number):
  location = f'{building.lower()} {number}'
  channel_name = f'{building.lower()}-{number}'
  category = get(ctx.guild.categories, name='location-channels')
  channel = get(category.text_channels, name=channel_name)
  if not channel:
    await leave_error(ctx, None)
    return
  
  # Check if user has the role
  role = get(ctx.guild.roles, name=location)
  if role not in ctx.author.roles:
    await leave_error(ctx, None)
    return
  
  # Remove the role from user
  await ctx.author.remove_roles(role, reason='left location')
  user = ctx.author.id
  if user in USER_ROLE:
    del USER_ROLE[user]
  embed = discord.Embed(title=f':white_check_mark: Location role for '
                              f'{location} removed!',
                        description=':wave: See you next time!',
                        color=0x57F287)
  await ctx.channel.send(embed=embed)
  await channel.send(f'{ctx.author.nick} has left!')


@leave.error
async def leave_error(ctx, error):
  embed = discord.Embed(title=f':x: Something went wrong!',
                        description=USAGE_MSGS[2],
                        color=0xED4245)
  await ctx.channel.send(embed=embed)

@client.command(name='list-info',
                help=f'Lists noise and busy-ness levels of all study '
                     f'locations\n'
                     f'{USAGE_MSGS[3]}',
                brief='Lists noise and busy-ness levels of all study locations')
async def list_info(ctx):
  # construct and send the info table
  info_table = '| Location | Noise | Busy-ness |\n' \
                 + '|----------|-------|-----------|\n'

  for location in LOCATIONS:
    location_string = location
    location_length = len(location_string)
    noise_level = str(LOCATIONS[location][0])
    busyness_level = str(LOCATIONS[location][1])

    # Add padding to location string
    while location_length < 8:
      location_string += ' '
      location_length += 1

    info_table += ('| ' + location_string + ' |   ' + noise_level +
                   '   |     ' + busyness_level + '     |\n')

  if len(LOCATIONS) == 0:
    info_table = 'No locations added yet.\nAdd the first location!'

  message = (f'Noise and Busy-ness Levels for each study location on a '
             f'scale 1 (lowest) to 5 (highest).\n'
             f'```{info_table}```'
             f'Note that a value of \"X\" denotes missing info. Be the '
             f'first to report noise or busy-ness info!')
  embed = discord.Embed(title=':information_source: Location Info',
                          description=message,
                          color=0x5865F2)
  await  ctx.channel.send(embed=embed)


@list_info.error
async def list_info_error(ctx, error):
  embed = discord.Embed(title=f':x: Something went wrong!',
                        description=USAGE_MSGS[3],
                        color=0xED4245)
  await ctx.channel.send(embed=embed)


@client.command(name='update-noise',
                help=f'Updates the noise level for a location.\n'
                     f'{USAGE_MSGS[4].replace("`", "")}',
                brief='Updates the noise level for a location.')
async def update_noise(ctx, building, number, val):
  # check if the location exists
  location = f'{building.lower()} {number}'
  if location not in LOCATIONS:
    await update_noise_error(ctx, None)
    return
  
  # check if val is between 1 and 5, inclusive
  val = int(val)
  if val < 1 or val > 5:
    await update_noise_error(ctx, None)
    return

  # update the location's noise level
  LOCATIONS[location] = [val, LOCATIONS[location][1]]

  embed = discord.Embed(title=(f':white_check_mark: Noise level updated to '
                              f'{val}!'),
                        description=(f':heart: Thanks for helping your peers '
                                     f'keep up to date with {location}!'),
                        color=0x57F287)
  await ctx.channel.send(embed=embed)


@update_noise.error
async def update_noise_error(ctx, error):
  info = 'Try updating the noise info for one of the following locations!```\n'
  for location in LOCATIONS.keys():
    info += f'{location}\n'
  info += '```'
  if len(LOCATIONS.keys()) == 0:
    info = ''
  embed = discord.Embed(title=f':x: Something went wrong!',
                        description=f'{USAGE_MSGS[4]}\n'
                                    f'{info}',
                        color=0xED4245)
  await ctx.channel.send(embed=embed)


@client.command(name='update-busy',
                help=f'Updates the busy-ness level for a location.\n'
                     f'{USAGE_MSGS[5].replace("`", "")}',
                brief='Updates the noise level for a location.')
async def update_busy(ctx, building, number, val):
  # check if the location exists
  location = f'{building.lower()} {number}'
  if location not in LOCATIONS:
    await update_busy_error(ctx, None)
    return
  
  # check if val is between 1 and 5, inclusive
  val = int(val)
  if val < 1 or val > 5:
    await update_busy_error(ctx, None)
    return

  # update the location's noise level
  LOCATIONS[location] = [LOCATIONS[location][0], val]

  embed = discord.Embed(title=(f':white_check_mark: Busy-ness level updated to '
                              f'{val}!'),
                        description=(f':heart: Thanks for helping your peers '
                                     f'keep up to date with {location}!'),
                        color=0x57F287)
  await ctx.channel.send(embed=embed)


@update_busy.error
async def update_busy_error(ctx, error):
  info = ('Try updating the busy-ness info for one of the following locations!'
          '```\n')
  for location in LOCATIONS.keys():
    info += f'{location}\n'
  info += '```'
  if len(LOCATIONS.keys()) == 0:
    info = ''
  embed = discord.Embed(title=f':x: Something went wrong!',
                        description=f'{USAGE_MSGS[5]}\n'
                                    f'{info}',
                        color=0xED4245)
  await ctx.channel.send(embed=embed)


@client.command(name='list-people',
                help=(f'Given a building code and room number, lists all '
                      f'people at that location\n'
                      f'{USAGE_MSGS[6]}'),
                brief='Lists people at a study location')
async def list_people(ctx, building, number):
  # validate building and number
  location = f'{building.lower()} {number}'
  channel_name = f'{building.lower()}-{number}'
  category = get(ctx.guild.categories, name='location-channels')
  channel = get(category.text_channels, name=channel_name)
  if not channel:
    await list_people_error(ctx, None)

  # list users with the role building-number
  people = ''
  role = get(ctx.guild.roles, name=location)
  members = role.members
  for member in members:
    people += (member.name + '\n')
  if len(members) == 0:
    people = 'None (Be the first to join!)'
  embed = discord.Embed(title=f':information_source: People at location '
                              f'\"{location}\"',
                        description=f'```{people}```',
                        color=0x5865F2)
  await ctx.channel.send(embed=embed)


@list_people.error
async def list_people_error(ctx, error):
  info = ('Try requesting the list of people at one of the following '
          'locations!```\n')
  for location in LOCATIONS.keys():
    info += f'{location}\n'
  info += '```'
  embed = discord.Embed(title=f':x: Something went wrong!',
                        description=f'{USAGE_MSGS[6]}\n'
                                    f'{info}',
                        color=0xED4245)
  await ctx.channel.send(embed=embed)


client.run(TOKEN)