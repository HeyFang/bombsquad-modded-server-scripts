# Released under the MIT License. See LICENSE for details.
#
"""Stats logger plugin for capturing game statistics (diagnostic + robust)."""

# ba_meta require api 9

from __future__ import annotations

import json
import os
import babase as ba
import bascenev1 as bs

from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Any

print("[StatsLogger] Importing stats_logger plugin...")


# ---------------------------------------------------------------------
# JSON Helpers
# ---------------------------------------------------------------------
def _load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        print(f"[StatsLogger] Warning: failed to load JSON at {path}")
        return {}


def _save_json(path: str, data: Dict[str, Any]) -> None:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        print(f"[StatsLogger] ERROR: failed to save JSON at {path}")


# ---------------------------------------------------------------------
# Plugin
# ---------------------------------------------------------------------
# ba_meta export babase.Plugin
class StatsLoggerPlugin(ba.Plugin):
    """
    Logs player account_id and short_name to a JSON file after each game.
    Also logs on player join for redundancy and prints diagnostics.
    """

    instance: "StatsLoggerPlugin" = None

    def __init__(self) -> None:
        super().__init__()
        StatsLoggerPlugin.instance = self

        self.stats_path = "ba_data/python/bautils/players/stats.json"
        # print(f"[StatsLogger] stats_path = {self.stats_path}")

        # Install wrappers and hooks
        try:
            self._patch_game_end()
        except Exception:
            print("[StatsLogger] ERROR installing end-game patches:")

        print("[StatsLogger] Plugin loaded successfully.")

    def _patch_game_end(self) -> None:
        """Wrap bascenev1.Activity.end (some flows call this directly)."""
        try:
            original = bs.GameActivity.end
        except Exception:
            print(
                "[StatsLogger] bs.Activity.end not found; skipping this patch."
            )
            return

        def wrapped_activity_end(
            activity: bs.GameActivity, *args, **kwargs
        ) -> Any:
            # print("[StatsLogger] wrapped Activity.end called; activity:", type(activity).__name__)
            LOGGED_FLAG = "stats_logged"

            if getattr(activity, LOGGED_FLAG, False):
                # print("[StatsLogger] Activity.end: stats already logged; skipping.")
                try:
                    return original(activity, *args, **kwargs)
                except Exception:
                    print("[StatsLogger] original Activity.end raised:")
                    return None

            setattr(activity, LOGGED_FLAG, True)

            try:
                # We log here because the stats objects are still guaranteed to be valid
                # and tied to the game's final state.
                self._attempt_log(activity, reason="GameActivity.end")
            except Exception:
                print(
                    "[StatsLogger] Error in stats logger after GameActivity.end:"
                )

            try:
                result = original(activity, *args, **kwargs)
            except Exception:
                print("[StatsLogger] original Activity.end raised:")
                return None

        bs.GameActivity.end = wrapped_activity_end
        # print("[StatsLogger] Patched bs.Activity.end")

    def _attempt_log(self, activity: bs.Activity, reason: str = "") -> None:
        """Always pull players from SessionPlayer list instead of activity.players."""
        # print(f"[StatsLogger] _attempt_log triggered by {reason}")

        session = bs.get_foreground_host_session()
        if session is None:
            print("[StatsLogger] No foreground session; cannot log players.")
            return

        players = list(session.sessionplayers)
        # print(f"[StatsLogger] SessionPlayers found: {len(players)}")

        stats = _load_json(self.stats_path)
        changed = False

        for sp in players:
            # for attr in dir(sp):
            #     if attr.startswith("_"):
            #         continue
            #     try:
            #         value = getattr(sp, attr)
            #     except Exception:
            #         value = "<ERROR>"
            #     print(f"{attr}: {value}")

            acc_id = None
            short_name = ""
            score = 0
            kills = 0
            deaths = 0

            try:
                stats_obj = session.stats
                records = stats_obj.get_records()
                sp_name = sp.getname(full=False, icon=False)
                record = records.get(sp_name)

                # Try match by raw keys too (just in case)
                # if record is None:
                #     for key, val in records.items():
                #         if isinstance(key, str) and key == sp_name:
                #             record = val
                #             break

                # print("SessionPlayer:", sp)
                # print("All records keys:", list(records.keys()))

                if record:
                    # print("PlayerRecord:", record.__dict__)
                    score = record.accumscore
                    kills = record.accum_kill_count
                    deaths = record.accum_killed_count

                    print(
                        f"[StatsLogger] Found record for {sp_name}: "
                        f"Score={score}, Kills={kills}, Deaths={deaths}"
                    )
                else:
                    print("PlayerRecord: <NONE> for ", sp_name)

            except Exception as e:
                print("[StatsLogger] ERROR reading Stats:", e)

            try:
                acc_id = sp.get_v1_account_id()  # REAL ACCOUNT ID
                dev = sp.inputdevice
                short_name = dev.get_v1_account_name(full=False)
            except Exception:
                acc_id = None
                short_name = ""

            if not acc_id:
                print(f"[StatsLogger] skipping (no acc_id): {sp}")
                continue

            prev = stats.get(acc_id)

            if prev is None:
                stats[acc_id] = {
                    "short_name": short_name,
                    "score": score,
                    "kills": kills,
                    "deaths": deaths,
                    "games": 1,
                }
                changed = True
                print(f"[StatsLogger] Will store: {short_name} ({acc_id})")
            else:
                # Ensure existing keys are present (for backwards compatibility if stats.json format changes)
                prev.setdefault("score", 0)
                prev.setdefault("kills", 0)
                prev.setdefault("deaths", 0)
                prev.setdefault("games", 0)

                # Update the name if it's different (optional, but robust)
                if prev["short_name"] != short_name:
                    prev["short_name"] = short_name
                    changed = True

                stats[acc_id]["score"] += score
                stats[acc_id]["kills"] += kills
                stats[acc_id]["deaths"] += deaths
                stats[acc_id]["games"] += 1

                # check if stats actually changed
                if score > 0 or kills > 0 or deaths > 0:
                    changed = True
                    print(
                        f"[StatsLogger] Updating stats for: {short_name} ({acc_id}): "
                        f"Score+{score}, Kills+{kills}, Deaths+{deaths}"
                    )
                else:
                    print(
                        f"[StatsLogger] No stat changes for: {short_name} ({acc_id})"
                    )

        if changed:
            _save_json(self.stats_path, stats)
            print("[StatsLogger] stats.json updated.")
        else:
            print("[StatsLogger] No changes; stats.json not updated.")
