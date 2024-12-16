import bascenev1 as bs


ros = bs.get_game_roster()

def hello():
    print("inside hello")
    bs.broadcastmessage(f"konnichiwa chibi!", clients=None, transient=True, color = (0,0.5,1))
    return None

def end(client_id):
    print("end is called")
    try:
        game = bs.get_foreground_host_activity()
        with game.context:
            game.end_game()
        for entity in ros:
            if entity["client_id"] == client_id:
                name = entity["players"][0]["name"]
                bs.broadcastmessage(f"{name} ended game", clients=None, transient=True, color = (0,0.5,1))
    except Exception as e:
        print(e)

    return None

def kick(msg, client_id):
    print("called kick")
    args = msg.split()
    rat = int(args[1])
    reason = " ".join(args[2:])

    try:
        bs.disconnect_client(rat, ban_time=60*5) #seconds
        for entity in ros:
            if entity["client_id"] == rat:
                nameRat = entity["display_string"]
                if entity["client_id"] == int(client_id):
                    name = entity["players"][0]["name"]
                    bs.broadcastmessage(f"{name} Kicked {nameRat}, reason: {reason}", transient=True, color=(0,0.5,1), clients=None)
                    print(f"{name} Kicked {nameRat}, reason: {reason}")
    except Exception as e:
        print(e)
    return None

def tint(msg):
    args = msg.split()
    r, g, b = float(args[1]), float(args[2]), float(args[3])
    try:
        activity = bs.get_foreground_host_activity()
        #print(dir(activity.globalsnode))
        activity.globalsnode.tint = (r, g, b)
    
    except Exception as e:
        print(e)
    return None

def nv():
    try:
        activity = bs.get_foreground_host_activity()
        activity.globalsnode.tint = (0.4, 0.4, 1)
        activity.globalsnode.ambient_color = (2, 2, 2)
    except Exception as e:
        print(e)
    return None

def pause(client_id):
    activity = bs.get_foreground_host_activity()
    if activity.globalsnode.paused == True:
        return None
    try:
        activity.globalsnode.paused = True
        for entity in ros:
            if entity["client_id"] == client_id:
                name = entity["players"][0]["name"]
                bs.broadcastmessage(f"{name} paused the game", transient=True, color=(0,0.5,1), clients=None)
    except Exception as e:
        print(e)
    return None

def resume(client_id):
    activity = bs.get_foreground_host_activity()
    if activity.globalsnode.paused == False:
        return None
    try:
        activity.globalsnode.paused = False
        for entity in ros:
            if entity["client_id"] == client_id:
                name = entity["players"][0]["name"]
                bs.broadcastmessage(f"{name} resumed the game", transient=True, color=(0,0.5,1), clients=None)
    except Exception as e:
        print(e)
    return None