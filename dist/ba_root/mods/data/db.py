import time
import os
from tinydb import TinyDB, Query
db_path = os.path.join(os.getcwd(), "ba_root/mods/data/database.json")
db = TinyDB(db_path)


banned = db.table("banned")
# warned = db.table("warned")
# muted = db.table("muted")


def pb_exists(tablename, pbid):
    table = db.table(tablename)
    entity = Query()
    return len(table.search(entity.pbid == pbid)) != 0


def duration_to_ms(duration: int):
    # 86400000 - 1 day
    curr = round(time.time() * 1000)
    release = curr + (86400000 * duration)
    return release


def ban(pbid: str, duration: int, reason: str = "no reason provided"):
    # pbid
    release = duration_to_ms(duration)
    release_in_format = time.ctime(release / 1000)
    duration = f"{str(duration)} (days)"
    
    # check if exists... then insert
    if pb_exists("banned", pbid):
        print(f"pbid ({pbid}) is already banned") 
    else:
        banned.insert({
            "pbid": pbid,
            "duration": duration,
            "release": release,
            "release_in_format": release_in_format,
            "reason": reason
        })
        print(f"Banned ({pbid}) for {duration} till {release_in_format}")