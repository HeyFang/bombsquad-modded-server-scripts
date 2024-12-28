import bascenev1 as bs
from tinydb import TinyDB, Query
import json
import os

# initialize the TinyDB database
db_path = os.path.join(os.getcwd(), 'ba_root/mods/db.json')
db = TinyDB(db_path)

def get_stats():
    try:
        ros = bs.get_game_roster()
        stats = bs.get_foreground_host_session().stats
        player_stats = stats.fetch_player_statistics()  

        combined_stats = []

        for entity in ros:
            for player in entity['players']:
                name = player['name']
                if name in player_stats:
                    pb_id = entity['account_id']
                    v2_id = entity['display_string']
                    kills = player_stats[name]['kills']
                    deaths = player_stats[name]['deaths']
                    score = player_stats[name]['score']

                    # check if the pb_id already exists in the database
                    Player = Query()
                    existing_record = db.search(Player.pb_id == pb_id)

                    if existing_record:
                        # update the existing record
                        new_kills = existing_record[0]['kills'] + kills
                        new_deaths = existing_record[0]['deaths'] + deaths
                        new_kd = new_kills / new_deaths if new_deaths != 0 else new_kills
                        db.update({
                            'games_played': existing_record[0]['games_played'] + 1,
                            'kills': new_kills,
                            'deaths': new_deaths,
                            'score': existing_record[0]['score'] + score,
                            'KD': new_kd
                        }, Player.pb_id == pb_id)
                    else:
                        # insert a new record
                        kd = kills / deaths if deaths != 0 else kills
                        combined_stats.append({
                            'pb_id': pb_id,
                            'v2_id': v2_id,
                            'games_played': 1,
                            'kills': kills,
                            'deaths': deaths,
                            'score': score,
                            'KD': kd
                        })
                else:
                    print(f"Player {name} not found in player_stats")

        # save data
        if combined_stats:
            db.insert_multiple(combined_stats)

        # calculate ranks based on scores
        all_records = db.all()
        sorted_records = sorted(all_records, key=lambda x: x['score'], reverse=True)
        top_100_records = sorted_records[:100]
        for rank, record in enumerate(top_100_records, start=1):
            db.update({'rank': rank}, Query().pb_id == record['pb_id'])

        # keep only top 100 records in the database
        db.purge()  # clear the database
        db.insert_multiple(top_100_records)  # insert top 100 records

        print("data in db.json:", db.all())

        with open(db_path, 'r') as json_file:
            data = json.load(json_file)

        with open(db_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        return combined_stats
    except Exception as e:
        print(e)
    return None