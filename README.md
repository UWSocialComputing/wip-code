# WIP Bot
**Team WIP**: Wanda Kuang, Ivy Zhou, & Patrick Ho
## About
WIP Bot is a Discord bot that helps facilitate collaboration between peers! Because studying can often be an isolating and unpleasant experience, especially in large classes, our project aims to leverage the existing platform and communities to achieve our project’s goals. WIP Bot helps with two main tasks: (1) finding other students to study with and (2) finding ideal study locations. With WIP Bot, users can add and tag themselves at specific locations on campus so that other students in the server can see where their peers are studying. Users can also report important information about each location, such as the noise and busy-ness level, so that other students can know which locations are suitable for their studying or collaborating needs. Currently, our Discord bot is hosted locally by a user, but we’re looking into the possibility of hosting it on Heroku or AWS. Our bot is implemented in Python using the discord.py library.
## Download and Host WIP Bot
To host WIP Bot, follow the following steps:
 - Clone this repo.
 - Create a Discord account.
 - Create an application using Discord's [developer portal](http://discordapp.com/developers/applications). Here's a [handy tutorial](https://realpython.com/how-to-make-a-discord-bot-python/#how-to-make-a-discord-bot-in-the-developer-portal) to reference!
 - Create a `.env` file containing `DISCORD_TOKEN=<token>` where `<token>` is your application's bot token.
 - Download the required dependencies via `pip install -r requirements. txt`
 - WIP Bot is ready to run! Use `python bot.py` to get started.
## Commands
### `/add-location`
 - Given a building code and room number, adds a new study location.
 - Usage: `/add-location building number` where `building` is a building name and `number` is a room number.

### `/tag-location`
- Given a building code and room number, gives you the role for that location,
- Usage: `/tag-location building number` where `building` is a building name and `number` is a room number.

### `/leave`
- Leaves a location, removing the location role for the location you are currently at.
- Usage: `/leave building number` where `building` is a building name and `number` is a room number. Note that you must be holding the location role for this location.

### `list-info`
- Lists noise and busy-ness levels of all study locations
- Usage: `/list-info` 

### `/update-noise`
- Updates the noise level for a location.
- Usage: `update-noise building number value` where `building` a building name and `number` is a room number for a location that exists, and `value` is the current noise level (between 1 and 5, inclusive) of that location.

### `/update-busy`
- Updates the busy-ness level for a location.
- Usage: `update-busy building number value` where `building` a building name and `number` is a room number for a location that exists, and `value` is the current \"busy-ness\" level (between 1 and 5, inclusive) of that location.

### `/list-people`
- Given a building code and room number, lists all people at that location
- Usage: `list-people building number` where `building` is a building name and `number` is a room number for a location exists

### `/init`
- Secret command! Resets WIP Bot for this server. Creates a new category for location channels, overwriting any existing location channels and deletes any building-related roles. **This command is intended to be used by server administrators only.**
- Usage: `init`.
