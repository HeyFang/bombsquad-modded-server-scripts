import babase as ba
import bascenev1 as bs
import json
import os
import commands.admin_commands as ac
import commands.user_commands as uc

def handle(msg: str, client_id):
    if not msg.startswith("/"):
        return msg

    args = msg.split()
    command = args[0].lstrip("/")
    
    admin_commands = {"kick", "end", "list", "maxplayers", "getmaxplayers", "remove", "restart", "tint", "nv", "time", "slowmo", "cl"}
    user_commands = {"list"}

    # check command existence
    if command not in admin_commands and command not in user_commands:
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
                try:
                    # dynamic function call based on command
                    getattr(ac, command)(args[1:], client_id)
                except AttributeError as e:
                    print(f"Error: {e}")
            else:
                if command in user_commands:
                    try:
                        getattr(uc, command)(args[1:], client_id)
                    except AttributeError as e:
                        print(f"Error: {e}")
                else:
                    # print(f"{entity['players'][0]['name']} is not an admin")
                    player_name = entity["players"][0]["name"]
                    bs.broadcastmessage(f"{player_name} - Access Denied. You're don't have admin permissions", transient=True, clients=[client_id])

    return msg