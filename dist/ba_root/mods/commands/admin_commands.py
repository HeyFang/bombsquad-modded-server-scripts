import _babase
import _bascenev1

import bacommon as bac
import babase as ba
import bascenev1 as bs
import bascenev1lib as bsl

from data import db

# /kick <client_id> <reason>
# /kick 113 being a weirdo
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


def __getpbid__(ros, target_id):
    return list(filter(lambda x: x != "", list(map((lambda x: x["account_id"] if x["client_id"] == int(target_id) else ""), ros)) ))[0]

def __getsessionid__(ros, target_id):
    return list(filter(lambda x: x != "", list(map((lambda x: x["players"][0]["id"] if x["client_id"] == int(target_id) else ""), ros)) ))[0]

def __getplayername__(ros, target_id):
    return list(filter(lambda x: x != "", list(map((lambda x: x["players"][0]["name"] if x["client_id"] == int(target_id) else ""), ros)) ))[0]

# /ban <client_id> <duration> <reason>
# /ban 113 30 says pineapple is better on pizza
# /ban 113 perma says pineapple should be topped with pizza crumbs
def ban(*params):
    args = params[0]
    admin_id = params[1]
    ros = params[2]
    
    try:
        target_id = args[0]
        duration = int(args[1])
        reason = " ".join(args[2:]) or "no reason"
        # pbid = list(filter(lambda x: x != "", list(map((lambda x: x["account_id"] if x["client_id"] == int(target_id) else ""), ros)) ))[0]
        pbid = __getpbid__(ros, target_id)
    except:
        return bs.broadcastmessage("Specify a valid ClientID (required) and Duration (required) to ban", transient=True, clients=[admin_id])
    
    try:
        db.ban(pbid, duration, reason)
        bs.disconnect_client(int(target_id), ban_time=60*5)
        bs.chatmessage(f"Client - {target_id} has been kicked for: {reason}")
    except Exception as e:
        print("there was an error while banning client")
        print(e)
    



def end(*params):
    # print('calling end')
    # print(bs.get_foreground_host_activity())
    # print(bs.get_foreground_host_activity().context)

    with bs.get_foreground_host_activity().context:
        bs.get_foreground_host_activity().end_game()
        bs.chatmessage(f"Admin Command Accepted. Game End")
    
    
# def list(*params):
#     ros = bs.get_game_roster()
#     # print(ros)
#     bs.chatmessage(f"  ClientID    SessionID   Name")
#     bs.chatmessage(f"----------------------------------------------------------")
#     for entity in ros:
#         if entity["client_id"] == -1:
#             pass
#         else:
#             player_name = entity["players"][0]["name_full"]
#             client_id = entity["client_id"]
#             session_id = entity["players"][0]["id"]
#             pbid = entity["account_id"]     # not sure if use this
            
#             bs.chatmessage(f"     {client_id}           {session_id}             {player_name[:15]}")
            
    
    # FORMAT PRESERVE
    # bs.chatmessage(f"  ClientID    SessionID   Name")
    # bs.chatmessage(f"----------------------------------------------------------")
    # bs.chatmessage(f"     113           0             Athena")
    # bs.chatmessage(f"     114           1             {"Yuzuru Asamiya asidj asidjasidsjdijasdjas idjaidaid ajd"[:15]}")
    # bs.chatmessage(f"     115           2             Chisato")
    
    
def maxplayers(*params):
    # args = params[0]
    args = next(iter(params), None)
    party_size = (next(iter(args), None))
    admin_id = params[1]

    try:
        if party_size == None:
            print("get the players")
            bs.broadcastmessage(f"Current party size is set to {str(bs.get_public_party_max_size())}", transient=True, color=(0, 0.5, 1))
        else:
            party_size = int(party_size)
            bs.set_public_party_max_size(party_size)
            bs.chatmessage(f"Max Player limit has been set to {str(party_size)}")
    except Exception as e:
        bs.broadcastmessage("syntax: /maxplayers <size>", transient=True, clients=[admin_id])
        print(e)

    
    
def remove(*params):
    args = params[0]
    target_id = int(args[0])
    ros = params[2]
    
    reason = " ".join(args[1:]) or "inactive"
    session_id = __getsessionid__(ros, target_id)
    player_name = __getplayername__(ros, target_id)
    
    
    for splayer in bs.get_foreground_host_session().sessionplayers:
        if session_id == splayer.id:
            try:
                splayer.remove_from_game()
                bs.chatmessage(f"{player_name} was removed for ehe reason: {reason}")
            except Exception as e:
                print(e)
    
    
    
                        
                        
                        
def restart(*params):
    bs.chatmessage("Restarting The Server...")
    try:
        ba.quit()
    except:
        bs.chatmessage("Restart Failed")
        

def tint(*params):
    args = params[0]
    r, g, b = float(args[0]), float(args[1]), float(args[2])
    
    with bs.get_foreground_host_activity().context:
        # print(bs.getnodes())
        for node in bs.getnodes():
            # if node.getnodetype() == "player":
            if node.getnodetype() == "globals":
                # node.tint(1.0, 1.0, 1.0)
                # print(dir(node))
                print(node.__setattr__("tint", (r, g, b)))
                
                
            # debugging stuff
            try:
                tint_value = node.__getattribute__("tint")
            except AttributeError:
                tint_value = "!exists"

            print(f"{node.getnodetype()} = {tint_value}")
            
            
            
def nv(*params):
    # try:
    #     activity = bs.get_foreground_host_activity()
    #     nv_tint = (0, 0.5, 1.0)
    #     activity.globalsnode.tint = (1, 1, 1) if activity.globalsnode.tint == nv_tint else nv_tint
    # except Exception as e:
    #     print(e)
    def is_close(a, b, tol=1e-5):
        return all(abs(x - y) < tol for x, y in zip(a, b))

    try:
        activity = bs.get_foreground_host_activity()
        nv_tint = (0.4, 0.4, 1.0)
        nv_ambient = (1.5, 1.5, 1.5)
        
        if is_close(activity.globalsnode.tint, nv_tint):
            activity.globalsnode.tint = (1, 1, 1)
            activity.globalsnode.ambient_color = (1, 1, 1)
            #print(activity.globalsnode.tint)
            bs.broadcastmessage("Night Mode off", transient=True, color=(0, 0.5, 1), clients=None)
        else:
            activity.globalsnode.tint = nv_tint
            activity.globalsnode.ambient_color = nv_ambient
            #print(activity.globalsnode.tint)
            bs.broadcastmessage("Night Mode on", transient=True, color=(0, 0.5, 1), clients=None)
    except Exception as e:
        print(e)
    return None
        
    
    
# the world shall freeze at command of the creator
def time(*params):
    args = params[0]
    client_id = params[1]
    
    try:
        activity = bs.get_foreground_host_activity()
    except Exception as e:
        print("unable to fetch activity")
        print(e)
    
    try:
        if args[0] == "stop":
            activity.globalsnode.paused = True
        elif args[0] == "start":
            activity.globalsnode.paused = False
    except IndexError as e:
        return bs.broadcastmessage(f"syntax: /time [stop | start]", transient=True, clients=[client_id])
    
    
def slowmo(*params):
    args = params[0]
    client_id = params[1]
    
    try:
        activity = bs.get_foreground_host_activity()
    except Exception as e:
        print("unable to fetch activity")
        print(e)
    
    try:
        if args[0] == "on":
            activity.globalsnode.slow_motion = True
        elif args[0] == "off":
            activity.globalsnode.slow_motion = False
    except IndexError as e:
        return bs.broadcastmessage(f"syntax: /slowmo [enable | disable]", transient=True, clients=[client_id])



def __getplayer__(target_id, ros):
    for player in ros:
        if player["client_id"] == target_id:
            for splayer in bs.get_foreground_host_session().sessionplayers:
                if player["players"][0]["id"] == splayer.id:
                    spaz = splayer.activityplayer
    return spaz
    
    
def kill(*params):
    args = params[0]
    ros = params[2]
    
    activity = bs.get_foreground_host_activity()
    
    if args[0] == "all":
        for player in activity.players:
            with activity.context:
                player.actor.shatter()
    else:
        target_id = int(args[0])
        spaz = __getplayer__(target_id, ros)
        
        try:
            with activity.context:
                spaz.actor.shatter()
        except Exception as e:
            print(e)



def curse(*params):
    args = params[0]
    ros = params[2]
    
    activity = bs.get_foreground_host_activity()
    
    if args[0] == "all":
        for player in activity.players:
            with activity.context:
                player.actor.curse()
    else:
        target_id = int(args[0])
        spaz = __getplayer__(target_id, ros)
        
        try:
            with activity.context:
                spaz.actor.curse()
        except Exception as e:
            print(e)



def gloves(*params):
    args = params[0]
    ros = params[2]
    
    activity = bs.get_foreground_host_activity()
    
    if args[0] == "all":
        for player in activity.players:
            with activity.context:
                player.actor.equip_boxing_gloves()
    else:
        target_id = int(args[0])
        spaz = __getplayer__(target_id, ros)
        
        try:
            with activity.context:
                spaz.actor.equip_boxing_gloves()
        except Exception as e:
            print(e)




# you're able to get a bomb but it works so...
# for all doesnt work, ima sleepy
def freeze(*params):
    args = params[0]
    ros = params[2]
    
    activity = bs.get_foreground_host_activity()
    
    target_id = int(args[0])
    spaz = __getplayer__(target_id, ros)
    
    try:
        with activity.context:
            spaz.actor.node.frozen = True
            bs.timer(6.0, (lambda: spaz.actor.node.__setattr__("frozen", False)))
    except Exception as e:
        print(e)



def thaw(*params):
    args = params[0]
    ros = params[2]
    
    activity = bs.get_foreground_host_activity()
    
    if args[0] == "all":
        for player in activity.players:
            with activity.context:
                player.actor.node.frozen = False
    else:
        target_id = int(args[0])
        spaz = __getplayer__(target_id, ros)
        
        try:
            with activity.context:
                spaz.actor.node.frozen = False
        except Exception as e:
            print(e)



        
def heal(*params):
    args = params[0]
    ros = params[2]
    
    activity = bs.get_foreground_host_activity()
    
    if args[0] == "all":
        for player in activity.players:
            with activity.context:
                player.actor.node.handlemessage(bs.PowerupMessage(poweruptype="health"))
    else:
        target_id = int(args[0])
        spaz = __getplayer__(target_id, ros)
        
        try:
            with activity.context:
                spaz.actor.node.handlemessage(bs.PowerupMessage(poweruptype="health"))
        except Exception as e:
            print(e)




def party_toggle(*params):
    # args = params[0]
    args = next(iter(params), None)
    
    try:
        if len(args) == 0:
            party_mode = bs.get_public_party_enabled()
            bs.broadcastmessage(f"Party mode is set to {"Public" if party_mode else "Private"}", transient=True, color=(1, 0.5, 1))
        elif args[0] == "pub" or args[0] == "public":
            bs.set_public_party_enabled(True)
            bs.broadcastmessage("Party mode set to Public", transient=True, color=(0, 0.5, 1))
        elif args[0] == "pvt" or args[0] == "private":
            bs.set_public_party_enabled(False)
            bs.broadcastmessage("Party mode set to Private", transient=True, color=(0, 0.5, 1))
    except Exception as e:
        print(e)
    return None



        














# testing command

def cl(*params):
    # args = params[0]
    # ros = params[2]
    # target_id = int(args[0])
    
    print('testing')
    print(db.pb_exists("banned", "pbtesting"))

    # for player in ros:
    #     if player["client_id"] == target_id:
    #         for splayer in bs.get_foreground_host_session().sessionplayers:
    #             if player["players"][0]["id"] == splayer.id:
    #                 try:
    #                     # print(dir(splayer.activityplayer))
    #                     # print(splayer.activityplayer.node)
    #                     # print(dir(splayer.activityplayer.node))
                        
    #                     with bs.get_foreground_host_activity().context:
    #                         player = splayer.activityplayer
    #                         # ga = bs.get_foreground_host_activity()
    #                         # spaz = ga.spawn_player(player)
    #                         # spaz.curse()
    #                         # print(player.actor)
    #                         print(dir(player.actor))
    #                         player.actor.shatter()
    #                 except Exception as e:
    #                     print(e)