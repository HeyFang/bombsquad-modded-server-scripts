import babase as ba
import bascenev1 as bs
import json
import os
import commands.admin_commands as ac

def handle(msg: str, client_id):
    if not msg.startswith("/"):
        return msg

    args = msg.split()
    command = args[0].lstrip("/")

    if command not in {"kick", "end", "list", "maxplayers", "getmaxplayers", "remove"}:
        bs.broadcastmessage("No such command", transient=True, clients=[client_id])
        return msg

    ros = bs.get_game_roster()
    for entity in ros:
        if entity["client_id"] == client_id:
            pbid = entity["account_id"]
            admin_path = os.path.join(os.getcwd(), "ba_root/mods/admin.json")
            with open(admin_path, "r") as file:
                admins = json.load(file)["admins"]

            if pbid in admins:
                print(f"{entity['players'][0]['name']} is an admin")
                try:
                    # dynamic function call based on command
                    getattr(ac, command)(args[1:])
                except AttributeError as e:
                    print(f"Error: {e}")
                    bs.broadcastmessage("Command function cannot be located", transient=True, clients=[client_id])
            else:
                bs.chatmessage(f"{entity['players'][0]['name']} Access Denied. You're not an admin")
                print(f"{entity['players'][0]['name']} is not an admin")

    return msg