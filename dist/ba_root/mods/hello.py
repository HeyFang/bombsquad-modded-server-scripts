import bascenev1 as bs

print("hello is called")

def hello():
    print("inside hello")

    try:
        game = bs.get_foreground_host_activity()
        with game.context:
            game.end_game()
        bs.broadcastmessage(f"konnichiwa chibi!", clients=None, transient=True, color = (0,0.5,1))
    except Exception as e:
        print(e)

    return None

def end(client_id):
    print("end is called")
    try:
        game = bs.get_foreground_host_activity()
        with game.context:
            game.end_game()
        bs.broadcastmessage(f"{client_id} ended game", clients=None, transient=True, color = (0,0.5,1))
    except Exception as e:
        print(e)

    return None
