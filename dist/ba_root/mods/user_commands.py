import bascenev1 as bs
from tinydb import TinyDB, Query
import os

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
    # stats of thyself if no arguments, else /stats <client_id>
    args = msg.split()
    # check if msg is /me or /stats
    if len(args) < 2:
        # get the entity of the client_id
        entity = get_entity(client_id)
        if entity:
            pb_id = entity["account_id"]
        else:
            bs.broadcastmessage("Player not found", transient=True, clients=[client_id], color=(1, 0, 0))
            return
    # else msg is /stats <client_id>
    else:
        args = msg.split()
        target = int(args[1])
        # get the entity of the target client_id
        entity = get_entity(target)
        if entity:
            pb_id = entity["account_id"]
        else:
            bs.broadcastmessage("Player not found", transient=True, clients=[client_id], color=(1, 0, 0))
            return
        
    # get the stats of the player
    Player = Query()
    record = db.search(Player.pb_id == pb_id)


    if record:
        name = record[0]['v2_id']
        games_played = record[0]['games_played']
        kills = record[0]['kills']
        deaths = record[0]['deaths']
        score = record[0]['score']
        rank = record[0]['rank']
        # calculate the kill/death ratio
        kd = kills / deaths if deaths > 0 else kills

        bs.broadcastmessage(f"{name} | Rank: {rank} | Score: {score} | Kills: {kills} | Deaths: {deaths} | K/D: {kd:.2f} | Games: {games_played}", transient=True, clients=None, color=(1, 1, 1))
    else:
        bs.broadcastmessage("Player not found", transient=True, clients=[client_id], color=(1, 0, 0))
    
    return None



        
