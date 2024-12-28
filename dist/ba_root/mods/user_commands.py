import bascenev1 as bs

def list(msg, client_id):
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

#def stats(msg, client_id):
#stats of thyself if no arguements, else /stats <client_id>