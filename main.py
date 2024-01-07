"""
The main code for the Master Hand Discord bot.
"""

import os
import json
import discord
from discord.utils import get
from dotenv import load_dotenv
import helpers


# Load the environment file.
load_dotenv()

# Retrieve and store the token and URL from the environment file.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
URL = os.getenv("URL")

# Configure and set the intents for the bot.
master_hand_intents = discord.Intents.default()
master_hand_intents.message_content = True
master_hand_intents.members = True
master_hand_intents.guilds = True
client = discord.Client(command_prefix="mh:", intents=master_hand_intents)


@client.event
async def on_ready():
    """
    Code to be run when the bot returns an on_ready event.
    """

    # Check for and create the necessary files for the bot.
    helpers.create_necessary_files()

    # Set the message to be sent when the bot logs in.
    logged_in_message = helpers.get_config("login_message")

    # Send the login message to the system channel for all of the bot's servers.
    for guild in client.guilds:
        channel = guild.system_channel

        # Attempt to send the login message.
        try:
            if logged_in_message:
                await channel.send(logged_in_message)
                helpers.write_log("on_ready", "success", "login message sent")
        except Exception as e:
            helpers.write_log(
                "on_ready",
                "failure",
                f"permission error: '{e}'",
            )
        finally:
            helpers.write_log("on_ready", "success", "bot is ready for use")


@client.event
async def on_message(message):
    """
    Code to be run when the bot returns a message event.
    """

    # Ignore messages from all bot users.
    if message.author.bot:
        return

    # Provide the configuration file contents.
    if message.content.startswith("mh:checkconfig"):
        # Notify the command runner that the bot is working.
        await message.channel.send("Checking configuration...")

        config = ""

        # Send the config file contents to the command runner.
        with open("master_hand_configuration.json", "r") as f:
            await message.channel.send(f"```{f.read()}```")

        helpers.write_log(
            "mh:config", "success", "bot has responded to the config command"
        )

        return

    # Help command.
    if message.content.startswith("mh:help"):
        command_role = helpers.get_config("command_role")

        help_message_intro = (
            "The command prefix is `mh:`, the following commands are available:\n\n"
        )

        help_message_commands = [
            "- `mh:hello` - A general testing command, the bot will respond with a message in the channel it was invoked.\n",
            "- `mh:checkconfig` - Returns the configuration JSON contents inside of a message in the channel it was invoked.\n",
            f"- `mh:setconfig` - [Requires role `{command_role}`] Sets a value to a key in the configuration JSON. If the key exists, the value will be updated. If the key does not exist, it will be created. Use `mh:checkconfig` to see the current configuration.\n",
            "- `mh:cleanup` - Checks all non-bot users in the server, if they do not have the `base_role` from the configuration JSON, then it will be added, and a message will be sent in the channel it was invoked to notify you of the users that were managed.\n",
            "- `mh:framedata` - Currently a work in progress. Eventually this will pull in the GIF and data from Ultimate Frame Data.\n",
            "- `mh:goodbot` - Lets me know that I am doing a good job.\n",
        ]

        help_message = help_message_intro

        for command in help_message_commands:
            help_message += command

        await message.channel.send(help_message)

    # General testing command.
    if message.content.startswith("mh:hello"):
        await message.channel.send("Hello!")
        helpers.write_log(
            "mh:hello", "success", "bot has responded to the hello command"
        )

        return

    # Create or set values in the configuration file.
    if message.content.startswith("mh:setconfig"):
        
        has_permissons = await check_permissions(client, message)

        if not has_permissons:
            await message.channel.send(
                "You do not have permissions to run this command!"
            )
            return

        # Remove the command from the message string.
        command = message.content.replace("mh:setconfig ", "")

        # Split the message by commas to get the arguments.
        set_config_params = command.split(",")

        # Store the number of arguments passed.
        number_of_arguments = len(set_config_params)

        # There should be two comma separated arguments.
        if number_of_arguments == 2:
            # Set and sanitize the key and value for readability.
            key_to_set = str(set_config_params[0]).strip()
            value_to_set = str(set_config_params[1]).strip()

            # Notify the command runner of the action being taken.
            await message.channel.send(f'Setting: `"{key_to_set}": "{value_to_set}"`')

            # Create or set the provided key to the provided value.
            helpers.set_configuration(key_to_set, value_to_set)
        # The wrong number of arguments was passed.
        else:
            # Notify the command runner the number of arguments is wrong.
            await message.channel.send(
                f"Whoa, whoa! {number_of_arguments} arguments submitted for `mh:setconfig`. 3 arguments expected!\n\nProper usage: `mh:setconfig key, value`\n\nFor a list of keys and values availble in the configuration file, run `mh:checkconfig`"
            )

    # Check for users missing the base role.
    if message.content.startswith("mh:cleanup"):
        # Set the base role to check for.
        base_role = helpers.get_config("base_role")

        # Set a scoped flag to use to determine if the base role is set.
        has_base_role = False

        # Set an empty string to hold memeber names for cleaned members.
        members_to_clean = ""

        # Check all memebers inside of the guild running this command.
        for member in message.guild.members:
            # Reset the flag to false for each iteration.
            has_base_role = False

            # Check all of the roles the memeber has for the base role.
            for role in member.roles:
                if role.name == base_role:
                    # Set the flag to True when the base role is found.
                    has_base_role = True

            # When a member is not a bot and doesn't have the base role, add it.
            if has_base_role is False and not member.bot:
                # Retrieve the role object based on the role name.
                base_role_name = discord.utils.get(member.guild.roles, name=base_role)

                if base_role_name:
                    # Add the role to the current member.
                    await member.add_roles(base_role_name)

                    helpers.write_log(
                        "mh:cleanup",
                        "success",
                        f"added {base_role_name} to {member.name}",
                    )

                    # Add the member's name to the list of cleaned members.
                    if members_to_clean != "":
                        members_to_clean += f", {member.name}"
                    else:
                        members_to_clean += f"{member.name}"
                else:
                    helpers.write_log(
                        "mh:cleanup",
                        "failure",
                        f"the request role could not be found: {base_role_name}",
                    )
                    await message.channel.send(
                        f"Could not find the role `{base_role_name}`"
                    )
                    break

        if members_to_clean:
            # List the base role and the members it was added to.
            await message.channel.send(
                f"Successfully added `{base_role}` to `{members_to_clean}`"
            )

            helpers.write_log(
                "mh:cleanup",
                "success",
                f"base role was cleaned up for: {members_to_clean}",
            )
        else:
            # Report that no members needed cleaning.
            await message.channel.send(
                f"No members were missing the base role `{base_role}`"
            )
            helpers.write_log("mh:cleanup", "failure", "base role was not cleaned up")

        helpers.write_log("mh:cleanup", "success", "member roles have been cleaned up")

    # Retrieve frame data from Ultimate Frame Data.
    if message.content.startswith("mh:framedata"):
        # WIP
        await message.channel.send("Work in progress")
        helpers.write_log(
            "mh:framedata", "success", "bot has responded to a request for framedata"
        )

        # frame_data_request = message.content.replace("/framedata", "")
        # await message.channel.send("Pulling...")
        # frame_data = pull_frame_data(URL, frame_data_request)
        # frame_data = frame_data[0:1000]

        # await message.channel.send("..." + str(frame_data))

        # write_log("mh:framedata", "success", "bot has provided frame data")

        return

    # Praise for the good bot.
    if message.content.startswith("mh:goodbot"):
        await message.channel.send(f"{message.author} I just do what I am told.")


@client.event
async def on_member_join(member):
    """
    Code to be run when a member joins the server.
    """

    helpers.write_log(
        "on_member_join", "process started", f"{member} has joined the server"
    )

    # Set the channle to the system channel.
    for guild in client.guilds:
        channel = guild.system_channel

    try:
        base_role = helpers.get_config("base_role")
        base_role_name = discord.utils.get(member.guild.roles, name=base_role)
        helpers.write_log(
            "on_member_join",
            "success",
            f"base role of {base_role_name} has been retrieved",
        )
    except Exception as error:
        helpers.write_log(
            "on_member_join",
            "failure",
            f"could not retrieve base role of {base_role_name}",
        )

    try:
        await member.add_roles(base_role_name)
        await channel.send(f"hello `{member}`, you are now a `{base_role_name}`")
        helpers.write_log(
            "on_member_join",
            "success",
            f"{member} was assigned the base role of {base_role_name}",
        )
    except Exception as error:
        helpers.write_log(
            "on_member_join",
            "failure",
            f"could not assign {base_role_name} to {member}: '{error}'",
        )


async def change_hands(client, message):
    """
    Code to change Master Hand into Crazy Hand, and vice versa.
    """

    # Currently the name change works, but the avatar change is not working.

    # current_hand = str(client.user).split("#")[0]
    # new_hand_name = "Crazy Hand" if current_hand == "Master Hand" else "Master Hand"
    # new_hand_image = (
    #     "crazy_hand.jpg" if current_hand == "master_hand.jpg" else "crazy_hand.jpg"
    # )

    # await client.user.edit(username=new_hand_name)
    # with open("assets/" + new_hand_image, "rb") as image:
    #     await client.user.edit(avatar=image)


async def check_permissions(client, message):
    """
    Checks if the current message author can run heightened commands.
    """

    # Set a flag for heightened commands.
    has_permission = False

    # Get the roles of the current message author.
    roles = message.author.roles

    # Retrieve the command role.
    command_role = helpers.get_config("command_role")

    # Check the author's roles for the command role
    for role in roles:
        if role.name == command_role:
            has_permission = True

    return has_permission


client.run(os.getenv("DISCORD_TOKEN"))
