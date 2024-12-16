import bascenev1 as bs

def list(*params):
    ros = bs.get_game_roster()
    bs.chatmessage(f"  ClientID    SessionID   Name")
    bs.chatmessage(f"----------------------------------------------------------")
    for entity in ros:
        if entity["client_id"] == -1:
            pass
        else:
            player_name = entity["players"][0]["name_full"]
            client_id = entity["client_id"]
            session_id = entity["players"][0]["id"]
            pbid = entity["account_id"]     # not sure if use this
            
            bs.chatmessage(f"     {client_id}           {session_id}             {player_name[:15]}")