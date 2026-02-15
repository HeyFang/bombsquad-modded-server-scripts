# Released under the MIT License. See LICENSE for details.
#
"""Handles All kinds of server utils provided by this project."""

# ba_meta require api 9
from . import settings

if settings.enableDiscordIntegration:
    print("--- Loading bautils package ---")  # Optional: Confirm this file runs

    try:
        # Import the discord server module to trigger its execution
        from .discord import discord_verify_server

        print(
            "    Successfully imported discord_verify_server from bautils/__init__.py"
        )
    except ImportError as e:
        print(
            f"    ERROR: Could not import discord_verify_server from bautils/__init__.py: {e}"
        )
    except Exception as e:
        print(
            f"    ERROR: An unexpected error occurred importing discord_verify_server from bautils/__init__.py: {e}"
        )
