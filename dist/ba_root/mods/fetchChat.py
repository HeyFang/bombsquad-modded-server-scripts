import babase as ba
import bascenev1 as bs
import json
import os
import hello

def filter_chat_message(msg: str, client_id: int) -> str | None:
    print(msg, client_id)
    
    if not msg.startswith("/"):
        return msg

    args = msg.split()
    command = args[0].lstrip("/").lower()

    admin_commands = {"kick", "hi", "end", "tint", "nv", "night", "pause", "resume", "sm", "slowmo", "epic", "maxplayers", "mp", "lm", "send", "announce", "quit", "restart"}
    user_commands = {"list", "me", "stats", "help"}

    if command not in admin_commands and command not in user_commands:
        bs.broadcastmessage("No such command", transient=True, clients=[client_id], color=(1,0,0))
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
                    match command:
                        case "list":
                            hello.list(client_id)
                        case "me" | "stats":
                            hello.stats(pbid)
                        case "help":
                            hello.help()
                        case _:
                            print("No such command")
                except AttributeError as e:
                    print(f"Error: {e}")

            elif pbid in admins:
                try:
                    match command:
                        case "kick":
                            hello.kick(msg, client_id)
                        case "hi":
                            hello.hello()
                        case "end":
                            hello.end(client_id)
                        case "tint":
                            hello.tint(msg)
                        case "nv" | "night":
                            hello.nv()
                        case "pause":
                            hello.pause(client_id)
                        case "resume":
                            hello.resume(client_id)
                        case "sm" | "slowmo" | "epic":
                            hello.slowmo()
                        case "maxplayers" | "mp":
                            hello.maxplayers(msg)
                        case "lm":
                            hello.past_msgs()
                        case "send" | "announce":
                            hello.send(msg)
                        case "quit" | "restart":
                            hello.quit(client_id)
                        case _:
                            print("No such command")
                except AttributeError as e:
                    print(f"Error: {e}")
            else:
                print(f"{entity['players'][0]['name']} is not an admin")

    return msg