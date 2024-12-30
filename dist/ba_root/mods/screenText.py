import bascenev1 as bs
import babase as ba
from tinydb import TinyDB, Query
import os

# initialize the TinyDB database
db_path = os.path.join(os.getcwd(), 'ba_root/mods/db.json')
db = TinyDB(db_path)

class PlayerTag:
    #gotta convert this to simple text node instead of array
    def __init__(self, player: bs._player, text: str, color=(1, 1, 1)):
        self.player = player
        self.text_nodes = []

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

            # Optional: Add animation to the text
            #animation_duration = 0.7
            #delay_offset = i * 0.05

            # bs.animate_array(
            #     node=letter_node,
            #     attr='color',
            #     size=3,
            #     keys={
            #         0.0 + delay_offset: (0.7, 0.7, 0.7),      # Start grey
            #         0.05 + delay_offset: (0.85, 0.85, 0.85), # Slightly brighter
            #         0.1 + delay_offset: (0.95, 0.95, 0.95),  # Even brighter
            #         0.15 + delay_offset: (1.0, 1.0, 1.0),    # Shine white
            #         0.2 + delay_offset: (0.95, 0.95, 0.95),  # Dim slightly
            #         0.25 + delay_offset: (0.85, 0.85, 0.85), # More dim
            #         0.3 + delay_offset: (0.7, 0.7, 0.7),     # Back to grey
            #         animation_duration + delay_offset: (0.7, 0.7, 0.7), # End grey (for looping)
            #     },
            #     loop=True
            # )
def ranks(self):
    player_rank_texts = {}
    Player = Query()
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
                    user_stats = db.search(Player.pb_id == pb_id)
                    if user_stats:
                        rank = user_stats[0].get('rank', 'N/A')
                        
                        # Remove the previous rank text node if it exists
                        if player in player_rank_texts:
                            for node in player_rank_texts[player].text_nodes:
                                node.delete()
                        
                        # Create a new PlayerTag above the player's head displaying their rank
                        player_rank_texts[player] = PlayerTag(player, f'#{rank}')

def top3_players():
    try:
        # Get all records from the database
        all_records = db.all()
        
        # Sort records by score in descending order
        sorted_records = sorted(all_records, key=lambda x: x['score'], reverse=True)
        
        # Get the top 3 records
        top3_records = sorted_records[:3] if sorted_records else []
        
        # Extract the v2_id of the top 3 players and remove the last character
        top1_v2_id = top3_records[0]['v2_id'][1:] if len(top3_records) > 0 else None
        top2_v2_id = top3_records[1]['v2_id'][1:] if len(top3_records) > 1 else None
        top3_v2_id = top3_records[2]['v2_id'][1:] if len(top3_records) > 2 else None
        
        #print(f"Top 3 players: {top1_v2_id}, {top2_v2_id}, {top3_v2_id}")
        return top1_v2_id, top2_v2_id, top3_v2_id
    except Exception as e:
        print(e)
    return None, None, None


t1, t2, t3 = top3_players()

# Function to create animated text nodes for each letter
def create_animated_text(letters, start_x, start_y, color_keys):
    letter_spacing = 10
    for i, letter in enumerate(letters):
        letter_position = (start_x + i * letter_spacing, start_y, 0)

        letter_node = bs.newnode(
            'text',
            attrs={
                'text': letter,
                'position': letter_position,
                'h_attach': 'right',
                'h_align': 'center',
                'v_attach': 'top',
                'shadow': 1.0,
                'flatness': 1.0,
                'color': (1, 1, 1, 1),  # Initial color
                'scale': 0.8,
            }
        )

        # Add animation to the letter node
        animation_duration = 0.7
        delay_offset = i * 0.05

        bs.animate_array(
            node=letter_node,
            attr='color',
            size=4,
            keys={
                0.0 + delay_offset: color_keys[0],      # Start color
                0.05 + delay_offset: color_keys[1],     # Slightly brighter
                0.1 + delay_offset: color_keys[2],      # Even brighter
                0.15 + delay_offset: color_keys[3],     # Shine
                0.2 + delay_offset: color_keys[4],      # Dim slightly
                0.25 + delay_offset: color_keys[5],     # More dim
                0.3 + delay_offset: color_keys[0],      # Back to start color
                animation_duration + delay_offset: color_keys[0], # End color (for looping)
            },
            loop=True
        )

# Define color keys for gold, silver, and bronze animations
gold_keys = [
    (1.0, 0.84, 0.0, 1.0),  # Gold
    (1.0, 0.9, 0.5, 1.0),   # Brighter gold
    (1.0, 0.95, 0.75, 1.0), # Even brighter gold
    (1.0, 1.0, 1.0, 1.0),   # Shine white
    (1.0, 0.95, 0.75, 1.0), # Dim slightly
    (1.0, 0.9, 0.5, 1.0),   # More dim
]

silver_keys = [
    (0.75, 0.75, 0.75, 1.0), 
    (0.85, 0.85, 0.85, 1.0),  
    (0.95, 0.95, 0.95, 1.0),  
    (1.0, 1.0, 1.0, 1.0),     
    (0.95, 0.95, 0.95, 1.0),  
    (0.85, 0.85, 0.85, 1.0),  
]

bronze_keys = [
    (0.8, 0.5, 0.2, 1.0),  
    (0.85, 0.55, 0.3, 1.0),  
    (0.9, 0.6, 0.4, 1.0),  
    (1.0, 1.0, 1.0, 1.0),  
    (0.9, 0.6, 0.4, 1.0),  
    (0.85, 0.55, 0.3, 1.0),  
]




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
                'scale': 1.4,
                'color': (0.4, 0.8, 1.0, 1.0),
                'text': "Welcome to our server. We hope you enjoy your stay here :D"
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
        # Add animation to the  node
        animation_duration = 0.7

        bs.animate_array(
            node=self.script2,
            attr='color',
            size=4,
            keys={
                0.0: silver_keys[0],      # Start color
                0.05: silver_keys[1],     # Slightly brighter
                0.1: silver_keys[2],      # Even brighter
                0.15: silver_keys[3],     # Shine
                0.2: silver_keys[4],      # Dim slightly
                0.25: silver_keys[5],     # More dim
                0.3: silver_keys[0],      # Back to start color
                animation_duration: silver_keys[0], # End color (for looping)
            },
            loop=True
        )


        # Create animated text for top1 with gold animation
        letters_t1 = list(t1)
        create_animated_text(letters_t1, start_x=-100, start_y=-125, color_keys=gold_keys)

        # Create animated text for top2 with silver animation
        letters_t2 = list(t2)
        create_animated_text(letters_t2, start_x=-100, start_y=-155, color_keys=silver_keys)

        # Create animated text for top3 with bronze animation
        letters_t3 = list(t3)
        create_animated_text(letters_t3, start_x=-100, start_y=-185, color_keys=bronze_keys) 
 
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

        ranks(self)
        

