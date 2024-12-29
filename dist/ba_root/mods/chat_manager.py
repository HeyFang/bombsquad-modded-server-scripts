import babase as ba
import bascenev1 as bs
import json
import os
import commands.admin_commands as ac
import commands.user_commands as uc
from tinydb import TinyDB, Query


def handle(msg: str, client_id):
    if not msg.startswith("/"):
        return msg

    args = msg.split()
    command = args[0].lstrip("/")
    
    admin_commands = [
        ["kick"], 
        ["ban"], 
        ["end"], 
        ["remove", "rm"], 
        ["list"], 
        ["maxplayers", "max"], 
        ["restart", "exit"], 
        ["tint"], 
        ["nv", "night"], 
        ["time"], 
        ["slowmo", "sm", "epic"], 
        ["kill"], 
        ["curse"], 
        ["gloves"], 
        ["freeze"], 
        ["heal"], 
        ["thaw"], 
        ["party", "partymode"],
        ["cl"], 
    ]
    user_commands = ["list"]     # dont need aliases for now + increases complexity
    
    # uhhh so in simple terms this extracts commands and aliases
    _admin_commands = list(map(lambda c: getattr(c, "__getitem__", "none")(0), admin_commands))
    aliases = sum(list(filter(lambda x: x != [], ( list(map(lambda a: a[1:] if len(a) > 1 else [], admin_commands)) ))), [])
    

    # check command existence
    if command not in _admin_commands and command not in user_commands and command not in aliases:
        bs.broadcastmessage("No such command", transient=True, clients=[client_id])
        return msg

    ros = bs.get_game_roster()
    for entity in ros:
        if entity["client_id"] == client_id:
            pbid = entity["account_id"]
            # admin_path = os.path.join(os.getcwd(), "ba_root/mods/admin.json")
            # with open(admin_path, "r") as file:
            #     admins = json.load(file)["admins"]
            
            customs_path = os.path.join(os.getcwd(), "ba_root/mods/data/customs.json")
            db = TinyDB(customs_path)
            admins = db.table("admins")
            admins = list(map(lambda chisai: chisai["pbid"], admins.all()))

            if command in user_commands:
                    try:
                        getattr(uc, command)(args[1:], client_id, ros)
                    except AttributeError as e:
                        print(f"Error: {e}")
            elif pbid in admins:
                # pointing the alias to command
                if command in aliases:
                    command = (list(filter(lambda f: f != [], list(map(lambda a: a[0] if command in a else [], admin_commands))) )[0])
                
                try:
                    # dynamic function call based on command
                    getattr(ac, command)(args[1:], client_id, ros)
                except AttributeError as e:
                    print(f"Error: {e}")
            else:
                # print(f"{entity['players'][0]['name']} is not an admin")
                player_name = entity["players"][0]["name"]
                bs.broadcastmessage(f"{player_name} - Access Denied. You don't have admin permissions", transient=True, clients=[client_id])

    return msg