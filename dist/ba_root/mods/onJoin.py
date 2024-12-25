import bascenev1 as bs
from roles import banlist



def add_chooser(self, sessionplayer: bs.SessionPlayer) -> None:
    print("onJoin.py is called")
    ros = bs.get_game_roster()
    #print(banlist)

    try:
        for player in ros:
            pbid = player['account_id']

            #for banned players
            if pbid in banlist:
                client_id = player['client_id']
                print(f"Account ID {pbid} is in the banlist.")
                bs.broadcastmessage(f"You are Banned, Contact the Admins for more information.", transient=True, clients=[client_id], color=(1, 0, 0))
                bs.disconnect_client(client_id, ban_time=60*60) #seconds
    except Exception as e:
        print(e)

    return 