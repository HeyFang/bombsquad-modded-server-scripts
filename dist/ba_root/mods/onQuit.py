import json
import os

admins_file = os.path.join(os.getcwd(), "ba_root/mods/admin.json")

def reset_muted():
    with open(admins_file, 'r') as file:
        data = json.load(file)
    print(f"Resetting muted list: {data['muted']}")
    
    if 'muted' in data:
        data['muted'] = []
    
    # Save the updated JSON data back to the file
    with open(admins_file, 'w') as file:
        json.dump(data, file, indent=4)
