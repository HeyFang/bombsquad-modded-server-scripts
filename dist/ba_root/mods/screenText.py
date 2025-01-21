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
                        'shadow': 0.5,
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

class Tag:
    # Convert this to a simple text node instead of array
    def __init__(self, player: bs._player, text: str, color=(1, 1, 1)):
        self.player = player
        self.text_nodes = []

        try:
            letter_spacing = 0.125
            start_offset = -(len(text) - 1) * letter_spacing / 2
            animation_duration = 0.3  # Duration of the animation loop

            # Define color keys for the animation
            color_keys = [
                (color[0], color[1], color[2], 1),  # Start color
                (min(color[0] + 0.2, 1), min(color[1] + 0.2, 1), min(color[2] + 0.2, 1), 1),  # Slightly brighter
                (min(color[0] + 0.4, 1), min(color[1] + 0.4, 1), min(color[2] + 0.4, 1), 1),  # Even brighter
                (min(color[0] + 0.6, 1), min(color[1] + 0.6, 1), min(color[2] + 0.6, 1), 1),  # Shine
                (min(color[0] + 0.4, 1), min(color[1] + 0.4, 1), min(color[2] + 0.4, 1), 1),  # Dim slightly
                (min(color[0] + 0.2, 1), min(color[1] + 0.2, 1), min(color[2] + 0.2, 1), 1),  # More dim
                (color[0], color[1], color[2], 1),  # Back to start color
            ]

            for i, letter in enumerate(text):
                letter_position = (start_offset + i * letter_spacing, 1.6, 0)

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
                        'shadow': 0.3,
                        'flatness': 1.0,
                        'color': color,
                        'scale': 0.01,
                        'h_align': 'center',
                    }
                )
                self.text_nodes.append(letter_node)
                math.connectattr('output', letter_node, 'position')

                # Animate the color of the letter node
                delay_offset = i * 0.05  # Increased delay offset for each letter
                bs.animate_array(
                    node=letter_node,
                    attr='color',
                    size=4,
                    keys={
                        0.0 + delay_offset: color_keys[0],      # Start color
                        0.2 + delay_offset: color_keys[1],     # Slightly brighter
                        0.4 + delay_offset: color_keys[2],      # Even brighter
                        0.6 + delay_offset: color_keys[3],     # Shine
                        0.8 + delay_offset: color_keys[4],      # Dim slightly
                        1.0 + delay_offset: color_keys[5],     # More dim
                        1.2 + delay_offset: color_keys[0],      # Back to start color
                        animation_duration + delay_offset: color_keys[0], # End color (for looping)
                    },
                    loop=True
                )

        except Exception as e:
            print(f"Error creating Tag for player {player}: {e}")


def ranks(self):
    player_rank_texts = {}
    tag = {}
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

                        if rank < 6 and player not in tag:
                            # Assign a tag based on the profile
                            profiles = player.sessionplayer.inputdevice.get_player_profiles()
                            tag_assigned = False
                            for profile_name, profile_data in profiles.items():
                                if profile_name.startswith("! "):
                                    crown = ba.charstr(ba.SpecialChar.CROWN)
                                    dragon = ba.charstr(ba.SpecialChar.DRAGON)
                                    helmet = ba.charstr(ba.SpecialChar.HELMET)
                                    fireball = ba.charstr(ba.SpecialChar.FIREBALL)
                                    ninja_star = ba.charstr(ba.SpecialChar.NINJA_STAR)
                                    
                                    tag_text = profile_name[2:].replace("/c", f"{crown}").replace("/d", f"{dragon}").replace("/h", f"{helmet}").replace("/f", f"{fireball}").replace("/n", f"{ninja_star}")
                                    # Get the player's profile color for the specific profile
                                    profile_color = profile_data['color']
                                    print(f"Profile: {profile_name}, Color: {profile_color}")
                                    tag[player] = Tag(player, tag_text, profile_color)
                                    tag_assigned = True
                                    break
                            if not tag_assigned:
                                tag[player] = Tag(player, "! <tag>", (1, 1, 1))
                        
                        match rank:
                            case None:
                                rank = " "
                                player_rank_texts[player] = PlayerTag(player, f'{rank}')
                            case 1:
                                player_rank_texts[player] = PlayerTag(player, f'{crown} {rank}', (1, 1, 0.0))
                            case 2:
                                player_rank_texts[player] = PlayerTag(player, f'{dragon} {rank}', (0.75, 0.75, 0.75))
                                #tag[player] = Tag(player, f"heyfang")
                            case 3:
                                player_rank_texts[player] = PlayerTag(player, f'{helmet} {rank}', (0.9, 0.4, 0.2))
                            case 4:
                                player_rank_texts[player] = PlayerTag(player, f'{fireball} {rank}', (0.8, 0.8, 0.8))
                            case 5:
                                player_rank_texts[player] = PlayerTag(player, f'{ninja_star} {rank}', (0.8, 0.8, 0.8))
                            
                            case _:
                                player_rank_texts[player] = PlayerTag(player, f'#{rank}')
    
    except Exception as e:
        print(f"Error updating ranks: {e}")
current_message_index = 0

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
                'scale': 1.6,
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
                'color': (0.0, 0.9, 0.9, 0.9),
                'text': "Still remember us? We're back after 4 years :D"
            },
        )
        
        
        self.script2 = bs.newnode(
            'text',
            attrs={
                'position': (0, 40),
                'h_attach': 'right',
                'h_align': 'right',
                'v_attach': 'bottom',
                # 'v_align': "center",
                'maxwidth': 300,
                'shadow': 0.5,
                # 'vr_depth': 390,
                'scale': 0.8,
                'color': (1, 1, 1, 1),
                'text': f"Scripts developed by "
            },
        )
        
        self.script2 = bs.newnode(
            'text',
            attrs={
                'position': (-15, 10),
                'h_attach': 'right',
                'h_align': 'right',
                'v_attach': 'bottom',
                # 'v_align': "center",
                'maxwidth': 300,
                'shadow': 0.5,
                # 'vr_depth': 390,
                'scale': 0.8,
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
                'position': (-150,-120),
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
                'position': (-150,-150),
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
                'position': (-150,-180),
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
            attrs={
                "position": (0, -220),
                "h_attach": "center",
                "h_align": "center",
                "v_attach": "center",
                "v_align": "center",
                "shadow": 0.5,
                "scale": 1.0,
                "color": (0.4, 1.0, 0.8, 1),
                "text": ""
            }
        )

        # List of messages to display
        messages = [
            "Join our Discord by clicking on stats button",
            "For ban related appeals contact the admins in Discord",
            "For complaints be sure to get ss and id of player using /pb <id>",
            "Eoni Discord Server: discord.gg/zcT3UnA",
            "Cyclones Discord Server: discord.gg/cv9r8Nq8fj",
            "use /rank or /me to check stats",
            "Ranks are assigned to only top 100 players"
        ]

        # Index to keep track of the current message
        

        def change_text():
            global current_message_index
            
            # Set the text to the current message
            self.loop_text.text = messages[current_message_index]
            
            # Animate the text to fade in and fade out
            animate(
                self.loop_text,
                'opacity',
                {
                    0: 0.0,    # Start fully transparent
                    1.0: 1.0,  # Fade in to fully opaque at 1 second
                    4.0: 1.0,  # Stay fully opaque until 4 seconds
                    5.0: 0.0   # Fade out to fully transparent at 5 seconds
                },
                loop=False
            )
            
            # Increment the message index and wrap around if necessary
            current_message_index = (current_message_index + 1) % len(messages)
            
            # Clear the text after it fades out
            bs.timer(5, ba.Call(lambda: self.loop_text.__setattr__("text", "")))

        # Set up a timer to change the text every 6 seconds
        bs.timer(6, ba.Call(change_text), repeat=True)
        
        
        

        
        

