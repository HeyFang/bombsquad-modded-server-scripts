from bascenev1._gameutils import animate
import bascenev1 as bs
import babase as ba
from tinydb import TinyDB, Query
import os
import random
import statsSys as st


# initialize the TinyDB database
db_path = os.path.join(os.getcwd(), 'ba_root/mods/db.json')
db = TinyDB(db_path)

class PlayerTag:
    # gotta convert this to simple text node instead of array
    def __init__(self, player: bs._player, text: str, color=(1, 1, 1)):
        self.player = player
        self.text_nodes = []

        try:
            letter_spacing = 0.125
            start_offset = -(len(text) - 1) * letter_spacing / 2

            for i, letter in enumerate(text):
                letter_position = (start_offset + i * letter_spacing, 1.3, 0)

                math = bs.newnode(
                    'math',
                    owner=self.player.node,
                    attrs={
                        'input1': letter_position,
                        'operation': 'add'
                    }
                )
                self.player.node.connectattr('position', math, 'input2')

                letter_node = bs.newnode(
                    'text',
                    owner=self.player.node,
                    attrs={
                        'text': letter,
                        'in_world': True,
                        'shadow': 1.0,
                        'flatness': 1.0,
                        'color': color,
                        'scale': 0.01,
                        'h_align': 'center',
                    }
                )
                self.text_nodes.append(letter_node)
                math.connectattr('output', letter_node, 'position')
        except Exception as e:
            print(f"Error creating PlayerTag for player {player}: {e}")


def ranks(self):
    player_rank_texts = {}
    try:
        ros = bs.get_game_roster()
        for team in self.teams:
            for player in team.players:
                if player.is_alive():
                    # Find the player's account ID from the roster
                    pb_id = None
                    for entity in ros:
                        if entity['client_id'] == player.sessionplayer.inputdevice.client_id:
                            pb_id = entity['account_id']
                            break
                    
                    if pb_id:
                        rank = st.get_rank(pb_id)
                        if rank is None:
                            rank = " "
                        
                        # Create a new PlayerTag above the player's head displaying their rank
                        player_rank_texts[player] = PlayerTag(player, f'#{rank}')
    except Exception as e:
        print(f"Error updating ranks: {e}")


def on_game_begin(self):
    # chars = ba.SpecialChar(64)
    
    with bs.get_foreground_host_activity().context:
        self.header1 = bs.newnode(
            'text',
            attrs={
                'position': (0, -50),
                'h_attach': 'center',
                'h_align': 'center',
                'v_attach': 'top',
                'maxwidth': 200,
                'shadow': 0.5,
                # 'vr_depth': 390,
                'scale': 1.4,
                'color': (0.0, 1.0, 1.0),
                'text': f"{ba.charstr(ba.SpecialChar.CROWN)} || EONI vs CYCLONES || {ba.charstr(ba.SpecialChar.CROWN)}",
                # 'transition': 'fade_in'
            },
        )
        
        self.header2 = bs.newnode(
            'text',
            attrs={
                'position': (0, -80),
                'h_attach': 'center',
                'h_align': 'center',
                'v_attach': 'top',
                # 'v_align': "center",
                'maxwidth': 300,
                'shadow': 0.5,
                # 'vr_depth': 390,
                'scale': 1.2,
                'color': (0.0, 0.9, 0.9, 0.9),
                'text': "Still remember us? We're back after 4 years :D"
            },
        )
        
        
        self.script2 = bs.newnode(
            'text',
            attrs={
                'position': (0, 30),
                'h_attach': 'right',
                'h_align': 'right',
                'v_attach': 'bottom',
                # 'v_align': "center",
                'maxwidth': 300,
                'shadow': 0.5,
                # 'vr_depth': 390,
                'scale': 0.7,
                'color': (1, 1, 1, 1),
                'text': f"Scripts developed by "
            },
        )
        
        self.script2 = bs.newnode(
            'text',
            attrs={
                'position': (-15, 5),
                'h_attach': 'right',
                'h_align': 'right',
                'v_attach': 'bottom',
                # 'v_align': "center",
                'maxwidth': 300,
                'shadow': 0.5,
                # 'vr_depth': 390,
                'scale': 0.7,
                'color': (1, 1, 1, 1),
                'text': f"{ba.charstr(ba.SpecialChar.CROWN)}Fang & Yuzuru{ba.charstr(ba.SpecialChar.MOON)}"
            },
        )
        self.top = bs.newnode(
            'text',
            attrs={
                'position': (-160,-90),
                'h_attach': 'right',
                'h_align': 'left',
                'v_attach': 'top',
                # 'v_align': "center",
                'maxwidth': 300,
                'shadow': 0.5,
                # 'vr_depth': 390,
                'scale': 0.7,
                'color': (1, 1, 1, 1),
                'text': f"{ba.charstr(ba.SpecialChar.TROPHY4)}Leaderboard{ba.charstr(ba.SpecialChar.TROPHY4)}"
            },
        )
        


        
        self.t3 = bs.newnode(
            'text',
            attrs={
                'position': (-130,-120),
                'h_attach': 'right',
                'h_align': 'left',
                'v_attach': 'top',
                # 'v_align': "center",
                'maxwidth': 25,
                'shadow': 0.5,
                # 'vr_depth': 390,
                'scale': 0.8,
                'color': (1, 1, 1, 1),
                'text': f"{ba.charstr(ba.SpecialChar.TROPHY3)}"
            },
        )
        self.t2 = bs.newnode(
            'text',
            attrs={
                'position': (-130,-150),
                'h_attach': 'right',
                'h_align': 'left',
                'v_attach': 'top',
                # 'v_align': "center",
                'maxwidth': 25,
                'shadow': 0.5,
                # 'vr_depth': 390,
                'scale': 0.8,
                'color': (1, 1, 1, 1),
                'text': f"{ba.charstr(ba.SpecialChar.TROPHY2)}"
            },
        )
        self.t1 = bs.newnode(
            'text',
            attrs={
                'position': (-130,-180),
                'h_attach': 'right',
                'h_align': 'left',
                'v_attach': 'top',
                # 'v_align': "center",
                'maxwidth': 25,
                'shadow': 0.5,
                # 'vr_depth': 390,
                'scale': 0.8,
                'color': (1, 1, 1, 1),
                'text': f"{ba.charstr(ba.SpecialChar.TROPHY1)}"
            },
        )
        self.loop_text = bs.newnode(
            "text",
            attrs = {
                "position": (0, -200),
                "h_attach": "center",
                "h_align": "center",
                "v_attach": "center",
                "v_align": "center",
                # "maxwidth": 300,
                "shadow": 0.5,
                "scale": 1.0,
                "color": (0.4, 1.0, 0.8, 1),
                "text": ""
            }
        )
        assert self.loop_text
        animate(
            self.loop_text,
            'opacity',
            {
                0: 0.0,    # Start fully transparent
                1.0: 1.0,  # Fade in to fully opaque at 1 second
                4.0: 1.0,  # Stay fully opaque until 4 seconds
                5.0: 0.0   # Fade out to fully transparent at 5 seconds
            },
            loop=True
        )

        def change_text():
            arr = [
                "Join the official discord community by clicking on stats button",
                "For ban related appeals contact the admins in discord server",
                "Come play minecraft with us in the cyclones discord community"
            ]
            key = round(random.random() * (len(arr) - 1))
            
            self.loop_text.text = arr[key]
            bs.timer(4, ba.Call( (lambda: self.loop_text.__setattr__("text", "")) ))
        
        bs.timer(6, ba.Call(change_text), repeat=True)
        
        
        

        
        ranks(self)
        

