import babase as ba
import bascenev1 as bs
import json
import os
import hello

def filter_chat_message(msg: str, client_id: int) -> str | None:
    print(msg, client_id)

    # Block messages from banned and muted players
    ros = bs.get_game_roster()
    for entity in ros:
        if entity["client_id"] == client_id:
            pbid = entity["account_id"]
            admin_path = os.path.join(os.getcwd(), "ba_root/mods/admin.json")

            with open(admin_path, "r") as file:
                data = json.load(file)
                banlist = data.get("banlist", [])
                muted = data.get("muted", [])
            if pbid in muted or pbid in banlist:
                return None
    
    # Normal messages
    if not msg.startswith("/"):
        return msg

    # Commands
    elif msg.startswith("/"):
        args = msg.split()
        command = args[0].lstrip("/").lower()

        admin_commands = {
            "kick": hello.kick,
            "hi": hello.hello,
            "end": hello.end,
            "tint": hello.tint,
            "nv": hello.nv, "night": hello.nv,
            "pause": hello.pause,
            "resume": hello.resume,
            "sm": hello.slowmo, "slowmo": hello.slowmo, "epic": hello.slowmo,
            "maxplayers": hello.maxplayers, "mp": hello.maxplayers,
            "lm": hello.past_msgs,
            "send": hello.send, "announce": hello.send,
            "quit": hello.quit, "restart": hello.quit,
            "remove": hello.remove, "rm": hello.remove,
            "ban": hello.ban,
            "unban": hello.unban,
            "party": hello.party_toggle, "partymode": hello.party_toggle,
            "bans": hello.bans, "banlist": hello.bans,
            "mute": hello.mute,
            "unmute": hello.unmute
        }

        user_commands = {
            "list": hello.list
        }

        if command not in admin_commands and command not in user_commands:
            bs.broadcastmessage("No such command", transient=True, clients=[client_id], color=(1, 0, 0))
            return msg

        ros = bs.get_game_roster()
        for entity in ros:
            if entity["client_id"] == client_id:
                pbid = entity["account_id"]
                admin_path = os.path.join(os.getcwd(), "ba_root/mods/admin.json")
                with open(admin_path, "r") as file:
                    admins = json.load(file)["admins"]

                if command in user_commands:
                    try:
                        func = user_commands[command]
                        #if command in {"me", "stats"}:
                        #    func(pbid)
                        if command in {"list"}:
                            func(client_id)
                    except AttributeError as e:
                        print(f"Error: {e}")

                elif pbid in admins:
                    try:
                        func = admin_commands[command]
                        if command in {"maxplayers", "mp", "tint", "send", "announce", "remove", "rm", "ban", "mute"}:
                            func(msg, client_id)
                        elif command in {"end", "pause", "resume", "quit", "restart"}:
                            func(client_id)
                        else:
                            func()
                    except AttributeError as e:
                        print(f"Error: {e}")
                else:
                    print(f"{entity['players'][0]['name']} is not an admin")
        return None
    return msg