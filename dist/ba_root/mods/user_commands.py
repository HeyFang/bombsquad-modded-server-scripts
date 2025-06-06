import bascenev1 as bs
from tinydb import TinyDB, Query
import os
import statsSys
import fetchChat

# initialize the TinyDB database
db_path = os.path.join(os.getcwd(), 'ba_root/mods/db.json')
db = TinyDB(db_path)

def get_entity(client_id):
    """Iterate through the game roster and return the entity with the given client_id."""
    ros = bs.get_game_roster()
    for entity in ros:
        if entity["client_id"] == client_id:
            return entity
    return None

def clients(msg, client_id):
    try:
        roster = bs.get_game_roster()
        message = f"{'ID':<9} |    {'Name':<12}\n" + "_" * 25 + "\n"
        for entry in roster:
            for player in entry['players']:
                message += f"{entry['client_id']:<9} {player['name']:<12}\n"
        bs.broadcastmessage(message, transient=True, color=(1,1,1), clients=[client_id])
    except Exception as e:
        print(e)
    return msg

def stats(msg, client_id):
    if len(msg.split()) < 2:
        urself = get_entity(client_id)
        if urself:
            pb_id = urself['account_id']
            specific_player_stats = statsSys.read_stats(pb_id)
            if specific_player_stats and len(specific_player_stats) == 6:
                v2_id, rank, score, kills, deaths, games_played = specific_player_stats
                #print(f"v2_id: {v2_id}, rank: {rank}, kills: {kills}, deaths: {deaths}, games_played: {games_played}")
                kd = kills / deaths if deaths > 0 else kills
                bs.broadcastmessage(f"{v2_id} | Rank: {rank} | Score: {score} | Kills: {kills} | Deaths: {deaths} | K/D: {kd:.2f} | Games Played: {games_played}", transient=True, color=(1,1,1), clients=None)
            else:
                bs.broadcastmessage("No stats found for player.", transient=True, color=(1,0,0), clients=[client_id])
        else:
            print("Player not found")
        return msg
    
    else:
        args = msg.split()
        target = int(args[1])
        target_entity = get_entity(target)
        if target_entity:
            target_pb = target_entity['account_id']
            specific_player_stats = statsSys.read_stats(target_pb)
            if specific_player_stats and len(specific_player_stats) == 6:
                v2_id, rank, score, kills, deaths, games_played = specific_player_stats
                #print(f"v2_id: {v2_id}, rank: {rank}, kills: {kills}, deaths: {deaths}, games_played: {games_played}")
                kd = kills / deaths if deaths > 0 else kills
                bs.broadcastmessage(f"{v2_id} | Rank: {rank} | Score: {score} | Kills: {kills} | Deaths: {deaths} | K/D: {kd:.2f} | Games Played: {games_played}", transient=True, color=(1,1,1), clients=None)        
            else:
                bs.broadcastmessage("No stats found for player.", transient=True, color=(1,0,0), clients=[client_id])
        else:
            print("Player not found")
        return msg


def pb(msg, client_id):
    if len(msg.split()) < 2:
        bs.broadcastmessage("/pb <id>", transient=True, color=(1, 0, 0), clients=[client_id])
        return None
    else:
        args = msg.split()
        target = int(args[1])
        target_entity = get_entity(target)
        if target_entity:
            target_pb = target_entity['account_id']
            target_v2 = target_entity['display_string']
            bs.broadcastmessage(f"{target_v2}: {target_pb}", transient=True, color=(0,0.5,1), clients=[client_id])
        else:
            bs.broadcastmessage(f"Player not found", transient=True, color=(1,0,0), clients=[client_id])
        return msg
        
def help(msg, client_id):
    message = ""
    try:
        # Split admin commands into chunks of 5 per line
        admin_commands = list(fetchChat.admin_commands.keys())
        admin_chunks = [admin_commands[i:i + 10] for i in range(0, len(admin_commands), 10)]
        message += "Admin Commands: " + "\n".join(", ".join(chunk) for chunk in admin_chunks) + "\n" + "\n"

        user_commands = list(fetchChat.user_commands.keys())
        user_chunks = [user_commands[i:i + 10] for i in range(0, len(user_commands), 10)]
        message += "User Commands: " + "\n".join(", ".join(chunk) for chunk in user_chunks) + "\n"
    except Exception as e:
        print(e)
    else:
        bs.broadcastmessage(message, transient=True, color=(1, 1, 1), clients=[client_id])
        return msg