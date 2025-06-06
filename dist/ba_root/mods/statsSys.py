import bascenev1 as bs
from tinydb import TinyDB, Query
import json
import os

# initialize the TinyDB database
db_path = os.path.join(os.getcwd(), 'ba_root/mods/db.json')
db = TinyDB(db_path)

def insert_stats():
    combined_stats = []
    try:
        # Fetching stats
        ros = bs.get_game_roster()
        stats = bs.get_foreground_host_session().stats
        player_stats = stats.get_records()  # dict: name -> PlayerRecord

        combined_stats = []

        for entity in ros:
            for player in entity['players']:
                name = player['name']
                if name in player_stats:
                    record = player_stats[name]
                    pb_id = entity['account_id']
                    v2_id = entity['display_string']

                    kills = record.kill_count
                    deaths = record.killed_count
                    score = record.score

                    Player = Query()
                    existing_record = db.search(Player.pb_id == pb_id)

                    if existing_record:
                        # Update existing record
                        db.update({
                            'games_played': existing_record[0]['games_played'] + 1,
                            'kills': existing_record[0]['kills'] + kills,
                            'deaths': existing_record[0]['deaths'] + deaths,
                            'score': existing_record[0]['score'] + score
                        }, Player.pb_id == pb_id)
                    else:
                        # Append new record only for insertion
                        combined_stats.append({
                            'pb_id': pb_id,
                            'v2_id': v2_id,
                            'games_played': 1,
                            'kills': kills,
                            'deaths': deaths,
                            'score': score
                        })
                else:
                    print(f"Player {name} not found in player_stats")

        # Save data
        if combined_stats:
            db.insert_multiple(combined_stats)

        # Calculate ranks based on scores for all players
        all_records = db.all()
        sorted_records = sorted(all_records, key=lambda x: x['score'], reverse=True)

        # Create a dictionary to store the ranks of all players
        ranks = {record['pb_id']: rank + 1 for rank, record in enumerate(sorted_records)}

        # Update ranks for currently playing players
        player_ids = [entity['account_id'] for entity in ros for player in entity['players']]
        for pb_id in player_ids:
            if pb_id in ranks:
                db.update({'rank': ranks[pb_id]}, Query().pb_id == pb_id)

        with open(db_path, 'r') as json_file:
            data = json.load(json_file)

        with open(db_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        return combined_stats
    except Exception as e:
        print(e)
    return combined_stats


def read_stats(pb_id=None):
    try:
        if pb_id:
            # Fetch stats for a specific player
            Player = Query()
            player_stats = db.search(Player.pb_id == pb_id)
            if player_stats:
                player_stats = player_stats[0]
                v2_id = player_stats.get('v2_id')
                rank = player_stats.get('rank')
                score = player_stats.get('score')
                kills = player_stats.get('kills')
                deaths = player_stats.get('deaths')
                games_played = player_stats.get('games_played')
                return v2_id, rank, score, kills, deaths, games_played
            else:
                print(f"No stats found for player with pb_id: {pb_id}")
                return " "
        else:
            # Fetch stats for all players
            all_stats = db.all()
            filtered_stats = []
            for player_stats in all_stats:
                v2_id = player_stats.get('v2_id')
                rank = player_stats.get('rank')
                score = player_stats.get('score')
                kills = player_stats.get('kills')
                deaths = player_stats.get('deaths')
                games_played = player_stats.get('games_played')
                filtered_stats.append((v2_id, rank, score, kills, deaths, games_played))
            return filtered_stats
    except Exception as e:
        print(e)
        return None

def get_top3():
    try:
        # Fetch all player stats
        all_stats = db.all()
        
        # Sort records by score in descending order
        sorted_records = sorted(all_stats, key=lambda x: x['score'], reverse=True)
        
        # Get the top 3 records
        top_3_records = sorted_records[:3] if sorted_records else []
        
        # Extract the v2_id of the top 3 players
        top_3_v2_ids = [record['v2_id'][1:] for record in top_3_records]
        
        # Return the top 3 v2_ids individually
        return (top_3_v2_ids[0] if len(top_3_v2_ids) > 0 else " ",
                top_3_v2_ids[1] if len(top_3_v2_ids) > 1 else " ",
                top_3_v2_ids[2] if len(top_3_v2_ids) > 2 else " ")
    except Exception as e:
        print(e)
        return " ", " ", " "
    
def get_rank(pb_id):
    try:
        # Fetch stats for a specific player
        Player = Query()
        player_stats = db.search(Player.pb_id == pb_id)
        if player_stats:
            player_stats = player_stats[0]
            rank = player_stats.get('rank')
            if rank > 100:
                return None
            return rank
        else:
            print(f"No stats found for player with pb_id: {pb_id}")
            return None
    except Exception as e:
        print(e)
        return None
