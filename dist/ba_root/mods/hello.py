import bascenev1 as bs
import babase as ba
from roles import banlist, save_banlist

#don't define activity variable at top to reduce redundancy; few cmds like 'end' wont work since Activity won't die

def get_entity(client_id):
    ros = bs.get_game_roster()
    for entity in ros:
        if entity["client_id"] == client_id:
            return entity
    return None

def hello():
    print()
    bs.broadcastmessage(f"konnichiwa chibi!", clients=None, transient=True, color=(0, 0.5, 1))
    return None

def end(client_id):
    try:
        game = bs.get_foreground_host_activity()
        with game.context:
            game.end_game()
        entity = get_entity(client_id)
        if entity:
            name = entity["players"][0]["name"]
            bs.broadcastmessage(f"{name} ended game", clients=None, transient=True, color=(0, 0.5, 1))
    except Exception as e:
        print(e)
    return None

def kick(msg, client_id):
    args = msg.split()
    rat = int(args[1])
    reason = " ".join(args[2:])

    try:
        rat_entity = get_entity(rat)
        admin_entity = get_entity(client_id)
        if rat_entity and admin_entity:
            nameRat = rat_entity["display_string"]
            name = admin_entity["players"][0]["name"]
            bs.broadcastmessage(f"{name} Kicked {nameRat}, reason: {reason}", transient=True, color=(0, 0.5, 1), clients=None)
            bs.disconnect_client(rat, ban_time=60*5)  # seconds
            print(f"{name} Kicked {nameRat}, reason: {reason}")
    except Exception as e:
        print(e)
    return None

def tint(msg):
    args = msg.split()
    r, g, b = float(args[1]), float(args[2]), float(args[3])
    try:
        # print(dir(activity.globalsnode))
        activity = bs.get_foreground_host_activity()
        activity.globalsnode.tint = (r, g, b)
    except Exception as e:
        print(e)
    return None

def nv():
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


def pause(client_id):
    activity = bs.get_foreground_host_activity()
    if activity.globalsnode.paused:
        return None
    try:
        activity.globalsnode.paused = True
        entity = get_entity(client_id)
        if entity:
            name = entity["players"][0]["name"]
            bs.broadcastmessage(f"{name} paused the game", transient=True, color=(0, 0.5, 1), clients=None)
    except Exception as e:
        print(e)
    return None

def resume(client_id):
    activity = bs.get_foreground_host_activity()
    if not activity.globalsnode.paused:
        return None
    try:
        activity.globalsnode.paused = False
        entity = get_entity(client_id)
        if entity:
            name = entity["players"][0]["name"]
            bs.broadcastmessage(f"{name} resumed the game", transient=True, color=(0, 0.5, 1), clients=None)
    except Exception as e:
        print(e)
    return None

def slowmo():
    try:
        activity = bs.get_foreground_host_activity()
        print(activity.globalsnode.slow_motion)
        if activity.globalsnode.slow_motion == True:
            activity.globalsnode.slow_motion = False
            bs.broadcastmessage("Epic mode off", transient=True, color=(0, 0.5, 1), clients=None)
        else:
            activity.globalsnode.slow_motion = True
            bs.broadcastmessage("Epic mode on", transient=True, color=(0, 0.5, 1), clients=None)
    except Exception as e:
        print(e)
    return None

def maxplayers(msg):
    args = msg.split()
    size = int(args[1])
    if 1 < size < 100:
        try:
            bs.set_public_party_max_size(size)
            #print(bs.get_public_party_max_size())
            bs.broadcastmessage(f"Max players set to {size}", transient=True, color=(0, 0.5, 1), clients=None)
        except Exception as e:
            print(e)
    else:
        bs.broadcastmessage("Invalid size. Must be between 2 and 99.", transient=True, color=(1, 0, 0), clients=None)
    return None

def past_msgs():
    #not sure this is good way to do it :/
    msgs = bs.get_chat_messages()
    for msg in msgs:
        bs.chatmessage(msg)
    return None

def send(msg):
    text = msg.split(" ", 1)[1]
    bs.broadcastmessage(text, transient=True, color=(0, 0.5, 1), clients=None)
    return None

def quit(client_id):
    try:
        entity = get_entity(client_id)
        if entity:
            name = entity["players"][0]["name"]
            bs.broadcastmessage(f"{name} restarted server", transient=True, color=(0, 0.5, 1), clients=None)
            ba.quit()
    except Exception as e:
        print(e)
    return None

def list(client_id):
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

def remove(msg, client_id):
    args = msg.split()
    rat = int(args[1])
    admin_entity = get_entity(client_id)
    rat_entity = get_entity(rat)

    try:
        session = bs.get_foreground_host_session()
        for i in session.sessionplayers:
            if i.inputdevice.client_id == rat:
                i.remove_from_game()
        if admin_entity and rat_entity:
            adminName = admin_entity["players"][0]["name"]
            ratName = rat_entity["players"][0]["name"]
            bs.broadcastmessage(f"{adminName} removed {ratName}", clients=None, transient=True, color=(0, 0.5, 1))
    except:
        return None

def party_toggle(msg):
    try:
        args = msg.split()
        if args[1] == "pub" or args[1] == "public":
            bs.set_public_party_enabled(True)
            bs.broadcastmessage("Party mode set to Public", transient=True, color=(0, 0.5, 1), clients=None)
        elif args[1] == "pvt" or args[1] == "private":
            bs.set_public_party_enabled(False)
            bs.broadcastmessage("Party mode set to Private", transient=True, color=(0, 0.5, 1), clients=None)
        print(bs.get_public_party_enabled())
    except Exception as e:
        print(e)
    return None

def ban(msg, client_id):
    args = msg.split()
    rat = int(args[1])
    reason = " ".join(args[2:])

    try:
        rat_entity = get_entity(rat)
        admin_entity = get_entity(client_id)
        if rat_entity and admin_entity:
            nameRat = rat_entity["display_string"]
            nameAdmin = admin_entity["players"][0]["name"]
            pbid = rat_entity["account_id"]
            print(pbid)
            if pbid not in banlist:
                banlist.append(pbid)
                save_banlist()  # Save the updated banlist to the file
                bs.broadcastmessage(f"{nameAdmin} banned {nameRat}, reason: {reason}", transient=True, color=(0, 0.5, 1), clients=None)
            else:
                print(f"User {pbid} is already in the banlist.")
                print(banlist)
    except Exception as e:
        print(e)
    return None

def unban(msg, client_id):
    #not with client_id, but with pbid...
    return None

def bans():
    try:
        bs.broadcastmessage(f"Banlist: {banlist}", transient=True, color=(0, 0.5, 1), clients=None)
    except Exception as e:
        print(e)
    return None