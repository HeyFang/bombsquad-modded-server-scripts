import bascenev1 as bs
from tinydb import TinyDB, Query
import json
import os

# Initialize the TinyDB database
db_path = os.path.join(os.getcwd(), 'ba_root/mods/db.json')
db = TinyDB(db_path)

def get_stats():
    try:
        ros = bs.get_game_roster()
        stats = bs.get_foreground_host_session().stats
        player_stats = stats.fetch_player_statistics()  

        #print("Player Stats:", player_stats)
        #print("Game Roster:", ros)

        combined_stats = []

        for entity in ros:
            for player in entity['players']:
                name = player['name']
                print(f"Checking player: {name}")
                if name in player_stats:
                    pb_id = entity['account_id']
                    v2_id = entity['display_string']
                    kills = player_stats[name]['kills']
                    deaths = player_stats[name]['deaths']
                    score = player_stats[name]['score']

                    # Check if the pb_id already exists in the database
                    Player = Query()
                    existing_record = db.search(Player.pb_id == pb_id)

                    if existing_record:
                        # Update the existing record
                        print(f"Updating existing record for pb_id: {pb_id}")
                        db.update({
                            'kills': existing_record[0]['kills'] + kills,
                            'deaths': existing_record[0]['deaths'] + deaths,
                            'score': existing_record[0]['score'] + score
                        }, Player.pb_id == pb_id)
                    else:
                        # Insert a new record
                        print(f"Inserting new record for pb_id: {pb_id}")
                        combined_stats.append({
                            'pb_id': pb_id,
                            'v2_id': v2_id,
                            'kills': kills,
                            'deaths': deaths,
                            'score': score
                        })
                else:
                    print(f"Player {name} not found in player_stats")

        print("Combined Stats:", combined_stats)

        # Save new combined stats to TinyDB
        if combined_stats:
            db.insert_multiple(combined_stats)

        # Verify that data is inserted
        print("Data in TinyDB:", db.all())

        # Pretty-print the JSON data
        with open(db_path, 'r') as json_file:
            data = json.load(json_file)

        with open(db_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        return combined_stats
    except Exception as e:
        print(e)
    return None
