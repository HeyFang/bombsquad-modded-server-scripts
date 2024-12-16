import _babase
import _bascenev1

import bacommon as bac
import babase as ba
import bascenev1 as bs

def kick(*params):
    args = params[0]
    admin_id = params[1]
    
    try:
        target_id = args[0]
        reason = " ".join(args[1:]) or "no reason"
    except:
        return bs.broadcastmessage("Specify a ClientID (required) and Reason (optional) to kick", transient=True, clients=[admin_id])
    
    try:
        # time in seconds
        bs.disconnect_client(int(target_id), ban_time=60*5)
        bs.chatmessage(f"Client - {target_id} has been kicked for: {reason}")
    except Exception as e:
        print("there was an error while kicking client")
        print(e)
    

def end(*params):
    # print('calling end')
    # print(bs.get_foreground_host_activity())
    # print(bs.get_foreground_host_activity().context)

    with bs.get_foreground_host_activity().context:
        bs.get_foreground_host_activity().end_game()
        bs.chatmessage(f"Admin Command Accepted. Game End")
    
    
def list(*params):
    ros = bs.get_game_roster()
    print(ros)
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
            
    
    # FORMAT PRESERVE
    # bs.chatmessage(f"  ClientID    SessionID   Name")
    # bs.chatmessage(f"----------------------------------------------------------")
    # bs.chatmessage(f"     113           0             Athena")
    # bs.chatmessage(f"     114           1             {"Yuzuru Asamiya asidj asidjasidsjdijasdjas idjaidaid ajd"[:15]}")
    # bs.chatmessage(f"     115           2             Chisato")
    
    
def maxplayers(*params):
    args = params[0]
    
    try:
        party_size = int(args[0])
    except TypeError:
        bs.screenmessage("Enter a valid integer limit")

    try:
        bs.set_public_party_max_size(party_size)
        bs.chatmessage(f"Max Player limit has been set to {str(party_size)}")
    except Exception as e:
        print(e)
        
        
def getmaxplayers(*params):
    bs.chatmessage(f"Max player limit is set to {str(bs.get_public_party_max_size())}")
    
    
def remove(*params):
    args = params[0]
    
    client_id = int(args[0])
    reason = " ".join(args[1:]) or "inactive"
    ros = bs.get_game_roster()
    for player in ros:
        if player["client_id"] == client_id:
            for splayer in bs.get_foreground_host_session().sessionplayers:
                if player["players"][0]["id"] == splayer.id:
                    try:
                        splayer.remove_from_game()
                        bs.chatmessage(f"{player["players"][0]["name"]} was removed for reason: {reason}")
                    except Exception as e:
                        print(e)
                        
                        
                        
def restart(*params):
    bs.chatmessage("Restarting The Server...")
    try:
        ba.quit()
    except:
        bs.chatmessage("Restart Failed")
        
