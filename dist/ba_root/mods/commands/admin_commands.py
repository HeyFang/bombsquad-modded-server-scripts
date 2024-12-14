import _babase
import _bascenev1

import babase as ba
import bascenev1 as bs

def kick(args):
    client_id = args[0]
    reason = " ".join(args[1:])
    
    try:
        # time in seconds
        bs.disconnect_client(int(client_id), ban_time=60*5)
        bs.chatmessage(f"Client ({client_id}) has been kicked")
    except Exception as e:
        print("there was an error while kicking client")
        print(e)
    

# fixing end comman atms
def end(*args):
    print('calling end')
    print(bs.get_foreground_host_activity())
    print(bs.get_foreground_host_activity().context)

    with bs.get_foreground_host_activity().context:
        bs.get_foreground_host_activity().end_game()
        bs.chatmessage(f"Admin Command Accepted. Game End")
    
    # bs.get_foreground_host_activity().end_game()
    
    # with _babase.ContextRef(bs.get_foreground_host_activity()):
    #     # bs.get_foreground_host_activity().end(None, 3.0)
    #     bs.get_foreground_host_activity().end_game()
    
    # bs.get_foreground_host_activity().end_game()
    
    
def list(*args):
    ros = bs.get_game_roster()
    print(ros)