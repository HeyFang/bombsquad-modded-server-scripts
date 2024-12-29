import bascenev1 as bs
from commands.admin_commands import kick
from data import db
import time

def __getclientid__(ros, pbid):
    return list(filter(lambda x: x != "", list(map((lambda x: x["client_id"] if x["account_id"] == pbid else ""), ros)) ))[0]

def _on_player_join(splayer):
    ros = bs.get_game_roster()
    pbid = splayer.get_v1_account_id()
    client_id = __getclientid__(ros, pbid)
    
    player_is_banned, player = db.is_banned(pbid)
    
    if player_is_banned:
        player = player[0]
        curr = round(time.time() * 1000)
        
        if curr >= player["release"]:
            db.unban(pbid)
        else:
            bs.broadcastmessage(f"You're currently banned for reason - {player["reason"]}", transient=True, clients=[client_id], color=(1, 0.3, 0.3))
            bs.broadcastmessage(f"Contact the server admins for appeal", transient=True, clients=[client_id], color=(1, 0.3, 0.3))
            bs.disconnect_client(int(client_id), ban_time=60*60)