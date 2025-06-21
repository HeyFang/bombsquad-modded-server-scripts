import json
import os

admins_file = os.path.join(os.getcwd(), "ba_root/mods/admin.json")

# Load the banlist from the file if it exists
if os.path.exists(admins_file):
    with open(admins_file, "r") as f:
        data = json.load(f)
        banlist = data.get("banlist", [])
        muted = data.get("muted", [])
else:
    muted = []
    banlist = []


def save_banlist():
    try:
        with open(admins_file, "r") as f:
            data = json.load(f)
        data["banlist"] = banlist
        with open(admins_file, "w") as f:
            json.dump(data, f, indent=4)  # Use indent=4 for pretty-printing
            f.flush()
        # print(f"Banlist saved to {admins_file}")
        print(f"Current banlist: {banlist}")
    except Exception as e:
        print(f"Failed to save banlist: {e}")
        print(f"Current banlist after exception: {banlist}")


def save_muted():
    try:
        with open(admins_file, "r") as f:
            data = json.load(f)
        data["muted"] = muted
        with open(admins_file, "w") as f:
            json.dump(data, f, indent=4)  # Use indent=4 for pretty-printing
            f.flush()
        # print(f"Muted list saved to {admins_file}")
        print(f"Current muted list: {muted}")
    except Exception as e:
        print(f"Failed to save muted list: {e}")
        print(f"Current muted list after exception: {muted}")


# Save muted list to the file
def save_muted():
    try:
        with open(admins_file, "r") as f:
            data = json.load(f)
        data["muted"] = muted
        with open(admins_file, "w") as f:
            json.dump(data, f, indent=4)  # Use indent=4 for pretty-printing
            f.flush()
        print(f"Current muted list: {muted}")
    except Exception as e:
        print(f"Failed to save muted list: {e}")
        print(f"Current muted list after exception: {muted}")


# Define roles as constants
USER = "user"
VIP = "vip"
ADMIN = "admin"
OWNER = "owner"

# Define all commands and their aliases
all_cmds = {
    "list": USER,
    "me": USER,
    "stats": USER,
    "rank": USER,
    "pb": USER,
    "help": USER,
    "commands": USER,
    "cmds": USER,
    "hi": VIP,
    "tint": VIP,
    "nv": VIP,
    "night": VIP,
    "sm": VIP,
    "slowmo": VIP,
    "epic": VIP,
    "info": VIP,
    "gp": VIP,
    "pause": VIP,
    "resume": VIP,
    "maxplayers": VIP,
    "mp": VIP,
    "lm": VIP,
    "send": VIP,
    "announce": VIP,
    "remove": VIP,
    "rm": VIP,
    "end": VIP,
    "kill": VIP,
    "freeze": VIP,
    "thaw": VIP,
    "gloves": VIP,
    "curse": VIP,
    "heal": VIP,
    "party": ADMIN,
    "partymode": ADMIN,
    "bans": ADMIN,
    "banlist": ADMIN,
    "mute": ADMIN,
    "unmute": ADMIN,
    "kick": ADMIN,
    "quit": ADMIN,
    "restart": ADMIN,
    "ban": OWNER,
    "unban": OWNER,
}


user_cmds = {cmd for cmd, role in all_cmds.items() if role == USER}
vip_cmds = user_cmds | {cmd for cmd, role in all_cmds.items() if role == VIP}
admin_cmds = vip_cmds | {cmd for cmd, role in all_cmds.items() if role == ADMIN}
owner_cmds = admin_cmds | {cmd for cmd, role in all_cmds.items() if role == OWNER}

# Role-to-command mapping
role_cmds = {USER: user_cmds, VIP: vip_cmds, ADMIN: admin_cmds, OWNER: owner_cmds}


# Function to get commands for a role
def get_commands_for_role(role: str):
    return role_cmds.get(
        role, user_cmds
    )  # Default to user commands if role is not found
