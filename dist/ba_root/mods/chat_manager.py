import babase as ba
import bascenev1 as bs
import json
import os
import commands.admin_commands as ac

def handle(msg: str, client_id):
	# /kick 113 idk no reason
	if msg.startswith("/"):
		args = msg.split()
		command = args[0].lstrip("/")
		
		commands_list = ["kick", "end", "ban"]
  
		ros = bs.get_game_roster()
		for entity in ros:
			if entity["client_id"] == client_id:
				pbid = entity["account_id"]
				admin_path = os.path.join(os.getcwd(), "ba_root/mods/admin.json")
				with open(admin_path, "r") as file:
					admins = json.load(file)["admins"]
     
				if pbid in admins:
					print(f"{entity["players"][0]["name"]} is an admin")
					# print(f"command: {command}")
					if command in commands_list:
						try:
							executor = getattr(ac, command)
							executor(args[1:])
						except AttributeError as e:
							print(f"Error: {e}")
							bs.broadcastmessage("Command function cannot be located", transient=True, clients=[client_id])
					else:
							bs.broadcastmessage("No such command", transient=True, clients=[client_id])
				else:
					if command not in commands_list:
						bs.broadcastmessage("No such command", transient=True, clients=[client_id])
					else:
						bs.chatmessage(f"{entity["players"][0]["name"]} Access Denied. You're not an admin")
						print(f"{entity["players"][0]["name"]} is not an admin")

	return msg


# def handle(msg: str, client_id):
# 	if msg.startswith("/getpb"):
# 		args = msg.split()
# 		command = args[0].lstrip("/")
  
# 		ros = bs.get_game_roster()
# 		for entity in ros:
# 			if entity["client_id"] == client_id:
# 				pbid = entity["account_id"]
# 				admin_path = os.path.join(os.getcwd(), "ba_root/mods/admin.json")
# 				with open(admin_path, "r") as file:
# 					admins = json.load(file)["admins"]

# 				if pbid in admins:
# 					print(f"{entity["players"][0]["name"]} is an admin")
# 					print(f"command: {command}")
# 				else:
# 					print(f"{entity["players"][0]["name"]} is not an admin")


# 	return msg