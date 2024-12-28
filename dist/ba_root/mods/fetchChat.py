import bascenev1 as bs
import json
import os
import admin_commands as ac
import user_commands as uc

# Load admin data once at the start
admin_path = os.path.join(os.getcwd(), "ba_root/mods/admin.json")
with open(admin_path, "r") as file:
    admin_data = json.load(file)
banlist = set(admin_data.get("banlist", []))
muted = set(admin_data.get("muted", []))
admins = set(admin_data.get("admins", []))

# Admin and user commands dictionaries
admin_commands = {
    "kick": ac.kick,
    "hi": ac,
    "end": ac.end,
    "tint": ac.tint,
    "nv": ac.nv, "night": ac.nv,
    "pause": ac.pause,
    "resume": ac.resume,
    "sm": ac.slowmo, "slowmo": ac.slowmo, "epic": ac.slowmo,
    "maxplayers": ac.maxplayers, "mp": ac.maxplayers,
    "lm": ac.past_msgs,
    "send": ac.send, "announce": ac.send,
    "quit": ac.quit, "restart": ac.quit,
    "remove": ac.remove, "rm": ac.remove,
    "ban": ac.ban,
    "unban": ac.unban,
    "party": ac.party_toggle, "partymode": ac.party_toggle,
    "bans": ac.bans, "banlist": ac.bans,
    "mute": ac.mute,
    "unmute": ac.unmute
}

user_commands = {
    "list": uc.list
}

def filter_chat_message(msg: str, client_id: int) -> str | None:
    print(msg, client_id)

    # Block messages from banned and muted players
    ros = bs.get_game_roster()
    for entity in ros:
        if entity["client_id"] == client_id:
            pbid = entity["account_id"]
            if pbid in muted or pbid in banlist:
                return None
    
    # Normal messages
    if not msg.startswith("/"):
        return msg

    # Commands
    args = msg.split()
    command = args[0].lstrip("/").lower()

    if command not in admin_commands and command not in user_commands:
        bs.broadcastmessage("No such command", transient=True, clients=[client_id], color=(1, 0, 0))
        return None

    for entity in ros:
        if entity["client_id"] == client_id:
            pbid = entity["account_id"]

            if command in user_commands:
                try:
                    user_commands[command](msg, client_id)
                except AttributeError as e:
                    print(f"Error: {e}")
                return None

            if pbid in admins:
                try:
                    admin_commands[command](msg, client_id)
                except AttributeError as e:
                    print(f"Error: {e}")
            else:
                print(f"{entity['players'][0]['name']} is not an admin")
            return None
    return msg