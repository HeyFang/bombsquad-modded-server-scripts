import bascenev1 as bs
import babase as ba
import json
import os 
import threading
from datetime import datetime, timezone

DATA_FILE = "player_information.json"

def _load_info() -> dict:
    """Loading the JSON file (create if missing)"""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
        
def _save_info(info: dict) -> None:
    """Saving the JSON file"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)

def _on_player_join(client_id: int) -> None:
    """Called when a player joins server"""
    try:
        v2_id = ba.get_client_account_id(client_id) #V2 id
    except Exception:
        v2_id = f"unknown-{client_id}"

    info = _load_info()

    if v2_id not in info:
        # Collect metadata
        ip_addr = None
        try:
            ip_addr = ba.get_client_public_address(client_id)
        except Exception:
            pass

        uuid = None
        try:
            uuid = ba.get_client_device_uuid(client_id)
        except Exception:
            pass

        record = {
            "first_seen": datetime.now(datetime.timezone.utc()).isoformat(),
            "ip": ip_addr,
            "uuid": uuid,
        }
        info[v2_id] = record
        _save_info(info)

class PlayerInfoPlugin:
    def __init__(self) -> None:
        ba.add_client_join_callback(_on_player_join)
