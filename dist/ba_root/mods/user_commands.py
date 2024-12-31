import bascenev1 as bs
from tinydb import TinyDB, Query
import os
import statsSys

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

def list(msg, client_id):
    try:
        roster = bs.get_game_roster()
        bs.broadcastmessage(f"{'ID':<2} | {'Name':<10} | {'Client_id':<9} | {'Pb-Id':<10}" + "\n" + "_" * 35, transient=True, color=(1,1,1), clients=[client_id])
        #bs.chatmessage(f"{'ID':<2} | {'Name':<10} | {'Client_id':<9} | {'Pb-Id':<10}" + "\n" + "_" * 35)
        for entry in roster:
            for player in entry['players']:
                bs.broadcastmessage(f"{player['id']:<4} {player['name']:<12} {entry['client_id']:<11} {entry['account_id']:<12}", transient=True, color=(1,1,1), clients=[client_id])
                #bs.chatmessage(f"{player['id']:<4} {player['name']:<12} {entry['client_id']:<11} {entry['account_id']:<12}")
    except Exception as e:
        print(e)
    return None

def stats(msg, client_id):
    if len(msg.split()) < 2:
        urself = get_entity(client_id)
        if urself:
            pb_id = urself['account_id']
            specific_player_stats = statsSys.read_stats(pb_id)
            if specific_player_stats:
                v2_id, rank, score, kills, deaths, games_played = specific_player_stats
                #print(f"v2_id: {v2_id}, rank: {rank}, kills: {kills}, deaths: {deaths}, games_played: {games_played}")
                kd = kills / deaths if deaths > 0 else kills
                bs.broadcastmessage(f"{v2_id} | Rank: {rank} | Score: {score} | Kills: {kills} | Deaths: {deaths} | K/D: {kd:.2f} | Games Played: {games_played}", transient=True, color=(1,1,1), clients=None)

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
            if specific_player_stats:
                v2_id, rank, score, kills, deaths, games_played = specific_player_stats
                #print(f"v2_id: {v2_id}, rank: {rank}, kills: {kills}, deaths: {deaths}, games_played: {games_played}")
                kd = kills / deaths if deaths > 0 else kills
                bs.broadcastmessage(f"{v2_id} | Rank: {rank} | Score: {score} | Kills: {kills} | Deaths: {deaths} | K/D: {kd:.2f} | Games Played: {games_played}", transient=True, color=(1,1,1), clients=None)        


        
