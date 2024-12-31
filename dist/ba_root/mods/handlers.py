import bascenev1 as bs
import bascenev1lib as bsl
import babase as ba
import random

def on_game_begins(self):
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
                'color': (0.4, 0.8, 1.0, 1.0),
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
                'position': (25, 75),
                'h_attach': 'left',
                'h_align': 'left',
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
                'position': (25, 50),
                'h_attach': 'left',
                'h_align': 'left',
                'v_attach': 'bottom',
                # 'v_align': "center",
                'maxwidth': 300,
                'shadow': 0.5,
                # 'vr_depth': 390,
                'scale': 0.8,
                'color': (1, 1, 1, 1),
                'text': f"{ba.charstr(ba.SpecialChar.CROWN)} Fang | {ba.charstr(ba.SpecialChar.MOON)} Yuzuru"
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
        
        
        
        bs.animate_array(node=self.loop_text, attr="color", size=3, 
                   keys= {
                        0.2: (0.4, 1.0, 0.8),
                        0.4: (0.4, 0.8, 1.0),
                        0.6: (0.4, 0.6, 0.8),
                        0.8: (0.4, 0.4, 0.6),
                        1.0: (0.4, 0.6, 0.4),
                        1.2: (0.4, 0.8, 0.6),
                        1.4: (0.4, 1.0, 0.8)
                   }, loop=True)