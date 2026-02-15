# File: bautils/discord/bot.py

import discord
from discord.ext import commands
from discord import app_commands  # Required for slash commands
import socket
import os
import json  # To format data for sending


# --- Configuration ---
BOT_TOKEN = 'YOUR_DISCORD_BOT_TOKEN_HERE'  # Replace with your actual bot token
GUILD_ID = (
    'YOUR_GUILD_ID_HERE'  # Replace with your actual Server ID (as an integer)
)
STAFF_ROLE_ID = 'YOUR_STAFF_ROLE_ID_HERE'  # Replace with your actual Staff Role ID (as an integer)
# This *must* match the path the BombSquad server will listen on
SOCKET_PATH = '/tmp/bombsquad_verify.sock'  # Example path in /tmp

# --- Bot Setup ---
intents = discord.Intents.default()  # Default intents are usually sufficient
# You might not need message_content if only using slash commands
# intents.message_content = True
bot = commands.Bot(
    command_prefix='.', intents=intents
)  # Prefix doesn't matter much for slash commands


# --- Bot Events ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    try:
        # --- SYNC TO A SPECIFIC GUILD (SERVER) ---
        guild_id = GUILD_ID
        guild = discord.Object(id=guild_id)
        # First, clear commands for this guild (optional, helps prevent duplicates)
        # bot.tree.clear_commands(guild=guild)
        # await bot.tree.sync(guild=guild)
        # Then sync
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} slash command(s) to guild {guild_id}")
        # ----------------------------------------

        # You can comment out global sync if only testing on one server
        # print("Syncing globally...")
        # synced_globally = await bot.tree.sync()
        # print(f"Synced {len(synced_globally)} command(s) globally.")

    except Exception as e:
        print(f"Error syncing slash commands: {e}")


# --- Slash Command ---
@bot.tree.command(
    name="verify",
    description="Verify admin status for the current BombSquad session.",
)
@app_commands.describe(
    shortname='Your current in-game BombSquad short name (case-sensitive)',
    client_id='Your current client ID shown in the verification message',
)
@app_commands.checks.has_role(STAFF_ROLE_ID)
async def verify(
    interaction: discord.Interaction, shortname: str, client_id: int
):
    """Handles the /verify slash command."""
    await interaction.response.defer(
        ephemeral=True
    )  # Acknowledge command privately

    # --- Unix Socket Communication ---
    try:
        # Create a Unix socket client
        client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        print(f"Attempting to connect to BombSquad server at {SOCKET_PATH}...")
        client_sock.connect(SOCKET_PATH)
        print("Connected to BombSquad server socket.")

        # Prepare data to send (e.g., as JSON)
        data_to_send = json.dumps(
            {
                'action': 'verify_admin',
                'client_id': client_id,
                'shortname': shortname,
            }
        )

        # Send data
        print(f"Sending verification request: {data_to_send}")
        client_sock.sendall(data_to_send.encode('utf-8'))

        # Optionally: Wait for a simple confirmation/response from the server
        # response = client_sock.recv(1024).decode('utf-8')
        # print(f"Received response from server: {response}")
        # if response == "OK":
        #    await interaction.followup.send(f"Verification request sent for {shortname} ({client_id}). Check in-game message.", ephemeral=True)
        # else:
        #    await interaction.followup.send(f"Server reported an issue verifying {shortname} ({client_id}). Details: {response}", ephemeral=True)

        # Simple confirmation for now
        await interaction.followup.send(
            f"Verification request sent for `{shortname}` (Client ID: `{client_id}`). Check in-game message.",
            ephemeral=True,
        )

    except FileNotFoundError:
        print(
            f"Error: Unix socket file not found at {SOCKET_PATH}. Is the BombSquad server running and listening?"
        )
        await interaction.followup.send(
            "❌ Error: Could not connect to the BombSquad server. Is it running?",
            ephemeral=True,
        )
    except ConnectionRefusedError:
        print(
            f"Error: Connection refused for {SOCKET_PATH}. Is the BombSquad server listening?"
        )
        await interaction.followup.send(
            "❌ Error: Connection refused by the BombSquad server.",
            ephemeral=True,
        )
    except Exception as e:
        print(f"An error occurred during socket communication: {e}")
        await interaction.followup.send(
            f"❌ An unexpected error occurred: {e}", ephemeral=True
        )
    finally:
        # Ensure the socket is closed
        if 'client_sock' in locals() and client_sock:
            client_sock.close()
            print("Socket connection closed.")


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    """Handles errors from slash commands."""
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message(
            "❌ You do not have the required 'Staff' role to use this command.",
            ephemeral=True,  # Send the message privately
        )
    else:
        # Fallback for other potential errors
        print(f"Unhandled slash command error: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ An unexpected error occurred.", ephemeral=True
            )
        else:
            await interaction.followup.send(
                "❌ An unexpected error occurred.", ephemeral=True
            )


# --- Run the Bot ---
if __name__ == "__main__":
    if BOT_TOKEN == 'YOUR_DISCORD_BOT_TOKEN_HERE':
        print(
            "ERROR: Please replace 'YOUR_DISCORD_BOT_TOKEN_HERE' with your actual bot token in bot.py"
        )
    else:
        bot.run(BOT_TOKEN)
