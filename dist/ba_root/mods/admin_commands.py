import bascenev1 as bs
import babase as ba
from roles import banlist, muted, save_banlist, save_muted
import threading
import json
import os

#don't define activity variable at top to reduce redundancy; few cmds like 'end' wont work since Activity won't die
#use both msg and client_id as arguments in chat commands even if you dont need them, (i did it so to avoid if-else conditions)
# hello sync

def get_entity(client_id):
    """Iterate through the game roster and return the entity with the given client_id."""
    ros = bs.get_game_roster()
    for entity in ros:
        if entity["client_id"] == client_id:
            return entity
    return None

def hello(msg, client_id):
    print(help(bs.newnode(text)))
    
    bs.broadcastmessage(f"konnichiwa chibi!", clients=None, transient=True, color=(0, 0.5, 1))
    return None

def end(msg, client_id):
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
    if len(msg.split()) < 2:
        bs.broadcastmessage("/kick <client_id>", transient=True, color=(1, 0, 0), clients=[client_id])
        return None
    args = msg.split()
    rat = int(args[1])
    reason = " ".join(args[2:])

    admin_path = os.path.join(os.getcwd(), "ba_root/mods/admin.json")
    with open(admin_path, "r") as file:
        admins = json.load(file)["admins"]
    
    try:
        rat_entity = get_entity(rat)
        admin_entity = get_entity(client_id)
        if rat_entity and admin_entity:
            # immune admins from being kicked
            ratPb = rat_entity["account_id"]
            if ratPb in admins:
                bs.broadcastmessage("You can't kick an admin", transient=True, color=(1, 0, 0), clients=[client_id])
                return None
            nameRat = rat_entity["display_string"]
            name = admin_entity["players"][0]["name"]
            bs.broadcastmessage(f"{name} Kicked {nameRat}, reason: {reason}", transient=True, color=(0, 0.5, 1), clients=None)
            bs.disconnect_client(rat, ban_time=60*5)  # seconds
            print(f"{name} Kicked {nameRat}, reason: {reason}")
    except Exception as e:
        print(e)
    return None

def tint(msg, client_id):
    if len(msg.split()) < 2:
        bs.broadcastmessage("/tint <r> <g> <b>", transient=True, color=(1, 0, 0), clients=[client_id])
        return None
    args = msg.split()
    r, g, b = float(args[1]), float(args[2]), float(args[3])
    try:
        # print(dir(activity.globalsnode))
        activity = bs.get_foreground_host_activity()
        activity.globalsnode.tint = (r, g, b)
    except Exception as e:
        print(e)
    return None

def nv(msg, client_id):
    def is_close(a, b, tol=1e-5):
        return all(abs(x - y) < tol for x, y in zip(a, b))

    try:
        activity = bs.get_foreground_host_activity()
        nv_tint = (0.5, 0.5, 1.0)
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


def pause(msg, client_id):
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

def resume(msg, client_id):
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

def slowmo(msg, client_id):
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

def maxplayers(msg, client_id):
    if len(msg.split()) < 2:
        bs.broadcastmessage("/maxplayers <size(int)>", transient=True, color=(1, 0, 0), clients=[client_id])
        return None
    args = msg.split()
    size = int(args[1])
    if 1 < size < 100:
        try:
            bs.get_foreground_host_session().max_players = size
            bs.set_public_party_max_size(size)
            #print(bs.get_public_party_max_size())
            bs.broadcastmessage(f"Max players set to {size}", transient=True, color=(0, 0.5, 1), clients=None)
        except Exception as e:
            print(e)
    else:
        bs.broadcastmessage("Invalid size. Must be between 2 and 99.", transient=True, color=(1, 0, 0), clients=None)
    return None

def past_msgs(msg, client_id):
    #not sure this is good way to do it :/
    msgs = bs.get_chat_messages()
    for msg in msgs:
        bs.chatmessage(msg)
    return None

def send(msg, client_id):
    text = msg.split(" ", 1)[1]
    bs.broadcastmessage(text, transient=True, color=(0, 0.5, 1), clients=None)
    return None

def quit(msg, client_id):
    try:
        entity = get_entity(client_id)
        if entity:
            name = entity["players"][0]["name"]
            bs.broadcastmessage(f"{name} restarted server", transient=True, color=(0, 0.5, 1), clients=None)
            ba.quit()
    except Exception as e:
        print(e)
    return None


def remove(msg, client_id):
    if len(msg.split()) < 2:
        bs.broadcastmessage("/remove <client_id>", transient=True, color=(1, 0, 0), clients=[client_id])
        return None
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

def party_toggle(msg, client_id):
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
    if len(msg.split()) < 2:
        bs.broadcastmessage("/ban <client_id> <reason>", transient=True, color=(1, 0, 0), clients=[client_id])
        return None
    args = msg.split()
    rat = int(args[1])
    reason = " ".join(args[2:])

    admin_path = os.path.join(os.getcwd(), "ba_root/mods/admin.json")
    with open(admin_path, "r") as file:
        admins = json.load(file)["admins"]

    if not reason:
        bs.broadcastmessage("A reason is required to ban a client.", transient=True, color=(1, 0, 0), clients=[client_id])
        bs.broadcastmessage("/ban <client_id> <reason>", transient=True, color=(0, 0.5, 1), clients=[client_id])
        return None

    try:
        rat_entity = get_entity(rat)
        admin_entity = get_entity(client_id)
        if rat_entity and admin_entity:
            nameRat = rat_entity["display_string"]
            nameAdmin = admin_entity["players"][0]["name"]
            pbid = rat_entity["account_id"]
            #print(pbid)

            if pbid in admins:
                bs.broadcastmessage("You can't ban an admin", transient=True, color=(1, 0, 0), clients=[client_id])
                return None
            
            if pbid not in banlist:
                banlist[pbid] = nameAdmin # add banned players pb n admins username
                save_banlist()  # Save the updated banlist to the file
                bs.broadcastmessage(f"{nameAdmin} banned {nameRat}, reason: {reason}", transient=True, color=(0, 0.5, 1), clients=None)
                bs.disconnect_client(rat, ban_time=60*60)  # seconds
            else:
                bs.broadcastmessage(f"User {pbid} is already in the banlist.", transient=True, color=(1, 0, 0), clients=[client_id])
                print(banlist)
    except Exception as e:
        print(e)
    return None

def unban(msg, client_id):
    if len(msg.split()) < 2:
        bs.broadcastmessage("/unban <pb-id>", transient=True, color=(1, 0, 0), clients=[client_id])
        return None
    
    args = msg.split()
    pbid = args[1]
    try:
        if pbid in banlist:
            admin_entity = get_entity(client_id)
            if admin_entity:
                adminName = admin_entity["players"][0]["name"]
            banned_by = banlist[pbid]  # Get the admin who banned the player
            del banlist[pbid]  # Remove from banlist
            save_banlist()  # Save the updated banlist to the file
            bs.broadcastmessage(f"{adminName} unbanned {pbid} (banned by {banned_by})", transient=True, color=(0, 0.5, 1), clients=None)
        else:
            bs.broadcastmessage(f"User {pbid} is not in the banlist.", transient=True, color=(1, 0, 0), clients=[client_id])
    except Exception as e:
        print(e)
    return None

def bans(msg, client_id):
    try:
        if not banlist:
            bs.broadcastmessage("Banlist is empty.", transient=True, color=(0, 0.5, 1), clients=[client_id])
            return None

        message = "Banlist:\n"
        for pbid, admin in banlist.items():
            message += f"{pbid} (banned by {admin})\n"
        bs.broadcastmessage(message, transient=True, color=(0, 0.5, 1), clients=None)
    except Exception as e:
        print(e)
    return None

def mute(msg, client_id):
    if len(msg.split()) < 2:
        bs.broadcastmessage("/mute <client_id>", transient=True, color=(1, 0, 0), clients=[client_id])
        return None
    args = msg.split()
    rat = int(args[1])

    try:
        rat_entity = get_entity(rat)
        admin_entity = get_entity(client_id)
        if rat_entity and admin_entity:
            nameRat = rat_entity["players"][0]["name"]
            nameAdmin = admin_entity["players"][0]["name"]
            pbid = rat_entity["account_id"]
            print(pbid)
            if pbid not in muted:
                muted.append(pbid)
                save_muted()  # Save the updated banlist to the file
                bs.broadcastmessage(f"{nameAdmin} muted {nameRat}", transient=True, color=(0, 0.5, 1), clients=None) # seconds
                #schedule unmute
                threading.Timer(60*5, unmute).start()
            else:
                bs.broadcastmessage(f"User {nameRat} already muted", transient=True, color=(1, 0, 0), clients=[client_id])
    except Exception as e:
        print(e)
    return None

def unmute(msg, client_id):
    #unmutes all
    try:
        if muted:
            muted.clear()
            save_muted()
            bs.broadcastmessage("Unmuted Player", transient=True, color=(0, 0.5, 1), clients=None)
        else:
            print("Muted list is already empty")
    except Exception as e:
        print(e)
    return None

def info(msg, client_id):
    if len(msg.split()) < 2:
        bs.broadcastmessage("/info <client_id>", transient=True, color=(1, 0, 0), clients=[client_id])
        return None
    args = msg.split()
    target = int(args[1])

    try:
        session_players = bs.get_foreground_host_session().sessionplayers
        target_player = None

        for player in session_players:
            if player.inputdevice.client_id == target:
                target_player = player
                break

        if target_player is None:
            bs.broadcastmessage("Invalid client_id", transient=True, color=(1, 0, 0), clients=[client_id])
            return None

        message = f"{'Sr.no':<9} |    {'Name':<12}\n" + "_" * 25 + "\n"
        i = 1
        for profile in target_player.inputdevice.get_player_profiles():
            try:
                message += f"{i:<9} {profile:<12}\n"
                i += 1
                #print(f"{profile}")
            except Exception as e:
                print(e)
        bs.broadcastmessage(message, transient=True, color=(1, 1, 1), clients=[client_id])
    except Exception as e:
        print(e)
    return None