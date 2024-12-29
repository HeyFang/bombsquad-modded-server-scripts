import bascenev1 as bs
import json

def list(*params):
    # ros = bs.get_game_roster()
    ros = params[2]
    print(ros)
    bs.chatmessage(f"  ClientID    SessionID   Name")
    bs.chatmessage(f"----------------------------------------------------------")
    for entity in ros:
        if entity["client_id"] == -1:
            pass
        else:
            try:
                player_name = entity["players"][0]["name_full"]
                session_id = entity["players"][0]["id"]
            except:
                entity["spec_string"] = json.loads(entity["spec_string"])
                player_name = entity["spec_string"]["n"]
                session_id = "--"
                
            
            client_id = entity["client_id"]
            pbid = entity["account_id"]     # not sure if use this
            
            bs.chatmessage(f"     {client_id}           {session_id}             {player_name[:15]}")