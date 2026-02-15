# Released under the MIT License. See LICENSE for details.
#
"""Settings for server utils provided by this project."""

# ba_meta require api 9

# ---- DISCORD SETTINGS ----
# Still in development and may have bugs, avoid using for now if not necessary... ill update it soon :>
# Add bot token and guild ID in Discord/bot.py if using Discord integration
enableDiscordIntegration: bool = False
enableDiscordAdminAuth: bool = False

# ---- BS SERVER SETTINGS ----
enableStatsLog: bool = True

# ---- PASSWORD AUTH SETTINGS ----
enablePasswordAuth: bool = True
adminPassword = 'dumbledore'

# ---- IP AUTH SETTINGS ----
enableIpAuth: bool = False
# ips are stored in hash form for privacy :>
authorizedAdminIPs: list[str] = [
    "17126921592780111236",  # Fang
    "5738055069092261189",  # another admin
]
