import babase as ba
import bascenev1 as bs
import json
import os
import commands as cmd

def filter_chat_message(msg: str, client_id: int) -> str:
    if not msg.startswith("/"):
        return msg

    args = msg.split()
    command = args[0].lstrip("/")

    if command not in {"kick", "hi"}:
        bs.broadcastmessage("No such command", transient=True, clients=[client_id], color=(1,0,0))
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
                    getattr(cmd, command)(args[1:])
                except AttributeError as e:
                    print(f"Error: {e}")
            else:
                print(f"{entity['players'][0]['name']} is not an admin")

    return msg