import babase as ba
import bascenev1 as bs

ros = bs.get_game_roster()


def kick(args: int):

    client_id = int(args[0])
    reason = " ".join(args[1:])

    try:
        bs.disconnect_client(client_id, ban_time=60*5) #seconds
        for entity in ros:
            if entity["client_id"] == client_id:
                name = entity["players"][0]["name"]
                bs.broadcastmessage(f"Kicked {name}, reason: {reason}", transient=True, color=(0,0.5,1), clients=None)
                print(f"Kicked {name}, reason: {reason}")
    except Exception as e:
        print(e)
    return None
