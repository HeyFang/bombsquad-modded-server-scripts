import bascenev1 as bs
import json
import os
import admin_commands as ac
import user_commands as uc
import roles as rl
print("✅ fetchchat loaded")
admin_commands = {
    "kick": ac.kick,
    "hi": ac.hello,
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
    "unmute": ac.unmute,
    "info": ac.info, "gp": ac.info,
    "kill": ac.kill,
    "curse": ac.curse,
    "gloves": ac.gloves,
    "freeze": ac.freeze,
    "thaw": ac.thaw,
    "heal": ac.heal
}

user_commands = {
    "list": uc.clients,
    "me": uc.stats, "stats": uc.stats, "rank": uc.stats,
    "pb": uc.pb,
    "help": uc.help, "commands": uc.help, "cmds": uc.help
}

def get_role(pbid: str) -> str:
    admin_path = os.path.join(os.getcwd(), "ba_root/mods/admin.json")
    with open(admin_path, "r") as file:
        data = json.load(file)
        if pbid in data.get("owners", {}):
            return "owner"
        elif pbid in data.get("admins", {}):
            return "admin"
        elif pbid in data.get("vips", {}):
            return "vip"
    return "user"


def filter_chat_message(msg: str, client_id: int) -> str | None:
    print(msg, client_id)

    # Block messages from banned and muted players
    ros = bs.get_game_roster()
    for entity in ros:
        if entity["client_id"] == client_id:
            pbid = entity["account_id"]
            role = get_role(pbid)
            
            # Block banned or muted players
            admin_path = os.path.join(os.getcwd(), "ba_root/mods/admin.json")
            with open(admin_path, "r") as file:
                data = json.load(file)
                banlist = data.get("banlist", [])
                muted = data.get("muted", [])
            if pbid in muted or pbid in banlist:
                return None
            
            # Get allowed commands for the role
            allowed_commands = rl.get_commands_for_role(role)

    
    # Normal messages
    if not msg.startswith("/"):
        return msg

    # Commands
    elif msg.startswith("/"):
        args = msg.split()
        command = args[0].lstrip("/").lower()

        # Check if the command is valid
        if command not in user_commands and command not in admin_commands:
            bs.broadcastmessage("Invalid command.", transient=True, clients=[client_id], color=(1, 0, 0))
            return None

        # Check if the command is allowed for the user's role
        if command not in allowed_commands:
            bs.broadcastmessage("You do not have permission to use this command.", transient=True, clients=[client_id], color=(1, 0, 0))
            return None

        # Execute the command
        try:
            if command in user_commands:
                func = user_commands[command]
            elif command in admin_commands:
                func = admin_commands[command]
            func(msg, client_id)
        except AttributeError as e:
            print(f"Error: {e}")
        return None
    return msg
