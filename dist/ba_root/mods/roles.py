import json
import os

admins_file = os.path.join(os.getcwd(), "ba_root/mods/admin.json")

# Load the banlist from the file if it exists
if os.path.exists(admins_file):
    with open(admins_file, 'r') as f:
        data = json.load(f)
        banlist = data.get("banlist", [])
        muted = data.get("muted", [])
else:
    muted = []
    banlist = []

def save_banlist():
    try:
        with open(admins_file, 'r') as f:
            data = json.load(f)
        data["banlist"] = banlist
        with open(admins_file, 'w') as f:
            json.dump(data, f, indent=4)  # Use indent=4 for pretty-printing
            f.flush()
        #print(f"Banlist saved to {admins_file}")
        print(f"Current banlist: {banlist}")
    except Exception as e:
        print(f"Failed to save banlist: {e}")
        print(f"Current banlist after exception: {banlist}")

def save_muted():
    try:
        with open(admins_file, 'r') as f:
            data = json.load(f)
        data["muted"] = muted
        with open(admins_file, 'w') as f:
            json.dump(data, f, indent=4)  # Use indent=4 for pretty-printing
            f.flush()
        #print(f"Muted list saved to {admins_file}")
        print(f"Current muted list: {muted}")
    except Exception as e:
        print(f"Failed to save muted list: {e}")
        print(f"Current muted list after exception: {muted}")