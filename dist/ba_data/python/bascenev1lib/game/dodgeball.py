# Dodge Ball

# Made by Pioos (IND_PIYUSH)


# ba_meta require api 9

from __future__ import annotations

from typing import TYPE_CHECKING


import bascenev1 as bs
import random
import logging
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.spazfactory import SpazFactory
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.actor.powerupbox import PowerupBoxFactory
from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, Sequence, Dict, Type, List, Optional, Union

def Chosenone(activity: bs.TeamGameActivity, from_opposite_team: bool = False, last_player: bs.Player | None = None) -> bs.Node | None: 
    valid_players = []

    for player in activity.players:
        if (player.actor is not None
                and isinstance(player.actor, PlayerSpaz)
                and player.actor.node is not None
                and player.actor.is_alive()):
            
            if from_opposite_team:
                if last_player is not None and player.team == last_player.team:
                    continue  # skip same-team players
            else:
                if last_player is not None and player == last_player:
                    continue  # skip last player

            valid_players.append(player)

    if not valid_players:
        return None

    chosen = random.choice(valid_players)
    return chosen.actor.node


class Icon(bs.Actor):
    """Creates in in-game icon on screen."""

    def __init__(
        self,
        player: Player,
        position: tuple[float, float],
        scale: float,
        *,
        show_lives: bool = True,
        show_death: bool = True,
        name_scale: float = 1.0,
        name_maxwidth: float = 115.0,
        flatness: float = 1.0,
        shadow: float = 1.0,
    ):
        super().__init__()

        self._player = player
        self._show_lives = show_lives
        self._show_death = show_death
        self._name_scale = name_scale
        self._outline_tex = bs.gettexture('characterIconMask')

        icon = player.get_icon()
        self.node = bs.newnode(
            'image',
            delegate=self,
            attrs={
                'texture': icon['texture'],
                'tint_texture': icon['tint_texture'],
                'tint_color': icon['tint_color'],
                'vr_depth': 400,
                'tint2_color': icon['tint2_color'],
                'mask_texture': self._outline_tex,
                'opacity': 1.0,
                'absolute_scale': True,
                'attach': 'bottomCenter',
            },
        )
        self._name_text = bs.newnode(
            'text',
            owner=self.node,
            attrs={
                'text': bs.Lstr(value=player.getname()),
                'color': bs.safecolor(player.team.color),
                'h_align': 'center',
                'v_align': 'center',
                'vr_depth': 410,
                'maxwidth': name_maxwidth,
                'shadow': shadow,
                'flatness': flatness,
                'h_attach': 'center',
                'v_attach': 'bottom',
            },
        )
        if self._show_lives:
            self._lives_text = bs.newnode(
                'text',
                owner=self.node,
                attrs={
                    'text': 'x0',
                    'color': (1, 1, 0.5),
                    'h_align': 'left',
                    'vr_depth': 430,
                    'shadow': 1.0,
                    'flatness': 1.0,
                    'h_attach': 'center',
                    'v_attach': 'bottom',
                },
            )
        self.set_position_and_scale(position, scale)

    def set_position_and_scale(
        self, position: tuple[float, float], scale: float
    ) -> None:
        """(Re)position the icon."""
        assert self.node
        self.node.position = position
        self.node.scale = [70.0 * scale]
        self._name_text.position = (position[0], position[1] + scale * 52.0)
        self._name_text.scale = 1.0 * scale * self._name_scale
        if self._show_lives:
            self._lives_text.position = (
                position[0] + scale * 10.0,
                position[1] - scale * 43.0,
            )
            self._lives_text.scale = 1.0 * scale

    def update_for_lives(self) -> None:
        """Update for the target player's current lives."""
        #bs.broadcastmessage(f"UPDATE FOR LIVES JUST GOT CALLED", clients=None, transient=True, color=(0, 0.5, 1))
        if self._player:
            lives = self._player.lives
        else:
            lives = 0
        if self._show_lives:
            if lives > 0:
                self._lives_text.text = 'x' + str(lives - 1)
            else:
                self._lives_text.text = ''
        if lives == 0:
            self._name_text.opacity = 0.2
            assert self.node
            self.node.color = (0.7, 0.3, 0.3)
            self.node.opacity = 0.2

    def handle_player_spawned(self) -> None:
        """Our player spawned; hooray!"""
        if not self.node:
            return
        self.node.opacity = 1.0
        self.update_for_lives()

    def handle_player_died(self) -> None:
        """Well poo; our player died."""
        #bs.broadcastmessage(f"HANDLE PLAYER DIED JUST GOT CALLED", clients=None, transient=True, color=(0, 0.5, 1))
        if not self.node:
            return
        if self._show_death:
            bs.animate(
                self.node,
                'opacity',
                {
                    0.00: 1.0,
                    0.05: 0.0,
                    0.10: 1.0,
                    0.15: 0.0,
                    0.20: 1.0,
                    0.25: 0.0,
                    0.30: 1.0,
                    0.35: 0.0,
                    0.40: 1.0,
                    0.45: 0.0,
                    0.50: 1.0,
                    0.55: 0.2,
                },
            )
            lives = self._player.lives
            if lives == 0:
                bs.timer(0.6, self.update_for_lives)

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            self.node.delete()
            return None
        return super().handlemessage(msg)

class PuckDiedMessage:
    """Inform something that a puck has died."""

    def __init__(self, puck: Puck):
        self.puck = puck



class Puck(bs.Actor):
    def __init__(self, position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()

        # Spawn just above the provided point.
        self._spawn_pos = (position[0], position[1] + 1.05, position[2])
        self.last_players_to_touch: Dict[int, Player] = {}
        self.scored = False
        assert activity is not None
        assert isinstance(activity, DodgeBallGame)

        self.current_aimer: AutoAimer | None = None

        pmats = [shared.object_material, activity.puck_material]
        self.node = bs.newnode('prop',
                               delegate=self,
                               attrs={
                                   'mesh': activity.puck_mesh,
                                   'color_texture': activity.puck_tex,
                                   'body': 'sphere',
                                   'reflection': 'soft',
                                   'reflection_scale': [0.2],
                                   'shadow_size': 0.6,
                                   'mesh_scale': 0.4,
                                   'body_scale': 1.07,
                                   'is_area_of_interest': True,
                                   'position': self._spawn_pos,
                                   'materials': pmats
                               })

        # Since it rolls on spawn, lets make gravity
        # to 0, and when another node (bomb/spaz)
        # touches it. It'll act back as our normie puck!
        bs.animate(self.node, 'gravity_scale', {0: -0.1, 0.2: 1}, False)
        # When other node touches, it realises its new gravity_scale

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            assert self.node
            self.node.delete()
            activity = self._activity()
            if activity and not msg.immediate:
                activity.handlemessage(PuckDiedMessage(self))

        # If we go out of bounds, move back to where we started.
        elif isinstance(msg, bs.OutOfBoundsMessage):
            assert self.node
            self.node.position = self._spawn_pos

        elif isinstance(msg, bs.HitMessage):
            assert self.node
            assert msg.force_direction is not None
            self.node.handlemessage(
                'impulse', msg.pos[0], msg.pos[1], msg.pos[2], msg.velocity[0],
                msg.velocity[1], msg.velocity[2], 1.0 * msg.magnitude,
                1.0 * msg.velocity_magnitude, msg.radius, 0,
                msg.force_direction[0], msg.force_direction[1],
                msg.force_direction[2])

            # If this hit came from a player, log them as the last to touch us.
            s_player = msg.get_source_player(Player)
            if s_player is not None:
                activity = self._activity()
                if activity:
                    if s_player in activity.players:
                        self.last_players_to_touch[s_player.team.id] = s_player
                        if self.current_aimer:
                            self.current_aimer.off()
                        target = Chosenone(activity, from_opposite_team=True, last_player=s_player)
                        self.current_aimer= AutoAimer(self.node, target)
        else:
            super().handlemessage(msg)


class Player(bs.Player['Team']):
    """Our player type for this game."""


class Team(bs.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.survival_seconds: int | None = None
        self.spawn_order: list[Player] = []


# ba_meta export bascenev1.GameActivity
class DodgeBallGame(bs.TeamGameActivity[Player, Team]):
    name = 'Dodge Ball'
    description = 'Hit the Enemies with ball'
    scoreconfig = bs.ScoreConfig(
        label='Survived', scoretype=bs.ScoreType.SECONDS, none_is_winner=True
    )
    available_settings = [
        bs.IntSetting(
            'Score to Win',
            min_value=1,
            default=1,
            increment=1,
        ),
        bs.IntChoiceSetting(
            'Time Limit',
            choices=[
                ('None', 0),
                ('1 Minute', 60),
                ('2 Minutes', 120),
                ('5 Minutes', 300),
                ('10 Minutes', 600),
                ('20 Minutes', 1200),
            ],
            default=0,
        ),
        bs.FloatChoiceSetting(
            'Respawn Times',
            choices=[
                ('Shorter', 0.25),
                ('Short', 0.5),
                ('Normal', 1.0),
                ('Long', 2.0),
                ('Longer', 4.0),
            ],
            default=1.0,
        ),
        bs.BoolSetting('Epic Mode', True),
        bs.BoolSetting('Icy Floor', True),
        bs.BoolSetting('Enable Bottom Credits', True),
    ]
    default_music = bs.MusicType.HOCKEY

    @classmethod
    def supports_session_type(cls, sessiontype: Type[bs.Session]) -> bool:
        return issubclass(sessiontype, bs.DualTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[bs.Session]) -> List[str]:
        return ['Football Stadium']

    def __init__(self, settings: dict):
        super().__init__(settings)
        shared = SharedObjects.get()
        self._scoreboard = Scoreboard()
        self._start_time: float | None = None
        self._vs_text: bs.Actor | None = None
        self._round_end_timer: bs.Timer | None = None
        self._lives_per_player = 1
        self._cheer_sound = bs.getsound('cheer')
        self._chant_sound = bs.getsound('crowdChant')
        self._dingsound = bs.getsound('dingSmall')
        self._foghorn_sound = bs.getsound('foghorn')
        self._swipsound = bs.getsound('swip')
        self._whistle_sound = bs.getsound('refWhistle')
        self.puck_mesh = bs.getmesh('shield')
        self.puck_tex = bs.gettexture('gameCircleIcon')
        self._puck_sound = bs.getsound('metalHit')
        self.puck_material = bs.Material()
        self.puck_material.add_actions(actions=(('modify_part_collision',
                                                 'friction', 0.5)))
        self.puck_material.add_actions(conditions=('they_have_material',
                                                   shared.pickup_material),
                                       actions=('modify_part_collision',
                                                'collide', True))
        self.puck_material.add_actions(
            conditions=(
                ('we_are_younger_than', 100),
                'and',
                ('they_have_material', shared.object_material),
            ),
            actions=('modify_node_collision', 'collide', False),
        )
        self.puck_material.add_actions(conditions=('they_have_material',
                                                   shared.footing_material),
                                       actions=('impact_sound',
                                                self._puck_sound, 0.2, 5))

        # Keep track of which player last touched the puck
        self.puck_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(('call', 'at_connect',
                      self._handle_puck_player_collide), ))

        # We want the puck to kill powerups; not get stopped by them
        self.puck_material.add_actions(
            conditions=('they_have_material',
                        PowerupBoxFactory.get().powerup_material),
            actions=(('modify_part_collision', 'physical', False),
                     ('message', 'their_node', 'at_connect', bs.DieMessage())))
        self._puck_spawn_pos: Optional[Sequence[float]] = None
        self._score_regions: Optional[List[bs.NodeActor]] = None
        self._puck: Optional[Puck] = None
        self._score_to_win = int(settings['Score to Win'])
        self._bombs_ = True
        self._time_limit = float(settings['Time Limit'])
        self._icy_flooor = bool(settings['Icy Floor'])
        self.credit_text = bool(settings['Enable Bottom Credits'])
        self._epic_mode = bool(settings['Epic Mode'])
        self._balance_total_lives = False
        self._solo_mode = False
        # Base class overrides.
        self.slow_motion = self._epic_mode
        self.default_music = (bs.MusicType.EPIC if self._epic_mode else
                              bs.MusicType.TO_THE_DEATH)
        
        self.player_node = None

    def get_instance_description(self) -> str | Sequence:
        return (
            'Last team standing wins.'
            if isinstance(self.session, bs.DualTeamSession)
            else 'Last one standing wins.'
        )

    def get_instance_description_short(self) -> str | Sequence:
        return (
            'last team standing wins'
            if isinstance(self.session, bs.DualTeamSession)
            else 'last one standing wins'
        )
    
    def on_player_join(self, player: Player) -> None:
        player.lives = self._lives_per_player
        player.icons = [Icon(player, position=(0, 50), scale=0.8)]
        if player.lives > 0:
            self.spawn_player(player)

        # Don't waste time doing this until begin.
        if self.has_begun():
            self._update_icons()

    def on_begin(self) -> None:
        super().on_begin()
        self._start_time = bs.time()
        self.setup_standard_time_limit(self._time_limit)
        self._puck_spawn_pos = self.map.get_flag_position(None)
        self._spawn_puck()
        self.player_node = Chosenone(self)

        aim = AutoAimer(self._puck.node, self.player_node)
        self._puck.current_aimer = aim
        # print(f"{self.player_node} : {self.node}")   
        
        if self.credit_text:
            t = bs.newnode('text',
                           attrs={'text': "IND_PIYUSH CREATIONS",  # Disable 'Enable Bottom Credits' when making playlist, No need to edit this lovely...
                                  'scale': 0.7,
                                  'position': (0, 90),
                                  'shadow': 0.5,
                                  'flatness': 1.2,
                                  'color': (1, 1, 1),
                                  'h_align': 'center',
                                  'v_attach': 'bottom'})
            
        if (
            isinstance(self.session, bs.DualTeamSession)
            and self._balance_total_lives
            and self.teams[0].players
            and self.teams[1].players
        ):
            if self._get_total_team_lives(
                self.teams[0]
            ) < self._get_total_team_lives(self.teams[1]):
                lesser_team = self.teams[0]
                greater_team = self.teams[1]
            else:
                lesser_team = self.teams[1]
                greater_team = self.teams[0]
            add_index = 0
            while self._get_total_team_lives(
                lesser_team
            ) < self._get_total_team_lives(greater_team):
                lesser_team.players[add_index].lives += 1
                add_index = (add_index + 1) % len(lesser_team.players)

        self._update_icons()

        # We could check game-over conditions at explicit trigger points,
        # but lets just do the simple thing and poll it.
        bs.timer(1.0, self._update, repeat=True)    

    def _update_icons(self) -> None:
        # pylint: disable=too-many-branches

        # In free-for-all mode, everyone is just lined up along the bottom.
        if isinstance(self.session, bs.FreeForAllSession):
            count = len(self.teams)
            x_offs = 85
            xval = x_offs * (count - 1) * -0.5
            for team in self.teams:
                if len(team.players) == 1:
                    player = team.players[0]
                    for icon in player.icons:
                        icon.set_position_and_scale((xval, 30), 0.7)
                        icon.update_for_lives()
                    xval += x_offs

        # In teams mode we split up teams.
        else:
            if self._solo_mode:
                # First off, clear out all icons.
                for player in self.players:
                    player.icons = []

                # Now for each team, cycle through our available players
                # adding icons.
                for team in self.teams:
                    if team.id == 0:
                        xval = -60
                        x_offs = -78
                    else:
                        xval = 60
                        x_offs = 78
                    is_first = True
                    test_lives = 1
                    while True:
                        players_with_lives = [
                            p
                            for p in team.spawn_order
                            if p and p.lives >= test_lives
                        ]
                        if not players_with_lives:
                            break
                        for player in players_with_lives:
                            player.icons.append(
                                Icon(
                                    player,
                                    position=(xval, (40 if is_first else 25)),
                                    scale=1.0 if is_first else 0.5,
                                    name_maxwidth=130 if is_first else 75,
                                    name_scale=0.8 if is_first else 1.0,
                                    flatness=0.0 if is_first else 1.0,
                                    shadow=0.5 if is_first else 1.0,
                                    show_death=is_first,
                                    show_lives=False,
                                )
                            )
                            xval += x_offs * (0.8 if is_first else 0.56)
                            is_first = False
                        test_lives += 1
            # Non-solo mode.
            else:
                for team in self.teams:
                    if team.id == 0:
                        xval = -50
                        x_offs = -85
                    else:
                        xval = 50
                        x_offs = 85
                    for player in team.players:
                        for icon in player.icons:
                            icon.set_position_and_scale((xval, 30), 0.7)
                            icon.update_for_lives()
                        xval += x_offs            

    def _get_spawn_point(self, player: Player) -> bs.Vec3 | None:
        del player  # Unused.

        # In solo-mode, if there's an existing live player on the map, spawn at
        # whichever spot is farthest from them (keeps the action spread out).
        if self._solo_mode:
            living_player = None
            living_player_pos = None
            for team in self.teams:
                for tplayer in team.players:
                    if tplayer.is_alive():
                        assert tplayer.node
                        ppos = tplayer.node.position
                        living_player = tplayer
                        living_player_pos = ppos
                        break
            if living_player:
                assert living_player_pos is not None
                player_pos = bs.Vec3(living_player_pos)
                points: list[tuple[float, bs.Vec3]] = []
                for team in self.teams:
                    start_pos = bs.Vec3(self.map.get_start_position(team.id))
                    points.append(
                        ((start_pos - player_pos).length(), start_pos)
                    )
                # Hmm.. we need to sort vectors too?
                points.sort(key=lambda x: x[0])
                return points[-1][1]
        return None                    
    
    def spawn_player(self, player: Player) -> bs.Actor:
        actor = self.spawn_player_spaz(player, self._get_spawn_point(player))
        if not self._solo_mode:
            bs.timer(0.3, bs.Call(self._print_lives, player))

        if self._bombs_:
            actor.bomb_count = 0   

        # If we have any icons, update their state.
        for icon in player.icons:
            icon.handle_player_spawned()
        return actor
    
    def _print_lives(self, player: Player) -> None:
        from bascenev1lib.actor import popuptext

        # We get called in a timer so it's possible our player has left/etc.
        if not player or not player.is_alive() or not player.node:
            return

        popuptext.PopupText(
            'x' + str(player.lives - 1),
            color=(1, 1, 0, 1),
            offset=(0, -0.8, 0),
            random_offset=0.0,
            scale=1.8,
            position=player.node.position,
        ).autoretain()

    def on_player_leave(self, player: Player) -> None:
        super().on_player_leave(player)
        player.icons = []

        # Remove us from spawn-order.
        if self._solo_mode:
            if player in player.team.spawn_order:
                player.team.spawn_order.remove(player)

        # Update icons in a moment since our team will be gone from the
        # list then.
        bs.timer(0, self._update_icons)

        # If the player to leave was the last in spawn order and had
        # their final turn currently in-progress, mark the survival time
        # for their team.
        if self._get_total_team_lives(player.team) == 0:
            assert self._start_time is not None
            player.team.survival_seconds = int(bs.time() - self._start_time)

    def _get_total_team_lives(self, team: Team) -> int:
        return sum(player.lives for player in team.players)            

    def _handle_puck_player_collide(self) -> None:
        collision = bs.getcollision()
        try:
            puck = collision.sourcenode.getdelegate(Puck, True)
            spaz = collision.opposingnode.getdelegate(PlayerSpaz,True)
            player = spaz.getplayer(Player, True)
            if spaz.is_alive():
                spaz.shatter()
                self.player_node = Chosenone(self)
                aim = AutoAimer(self._puck.node, self.player_node)
                self._puck.current_aimer = aim
        except bs.NotFoundError:
            return
        

        puck.last_players_to_touch[player.team.id] = player   

    def on_transition_in(self) -> None:
        super().on_transition_in()
        activity = bs.getactivity()
        if self._icy_flooor:
            activity.map.is_hockey = True

        

    def handlemessage(self, msg: Any) -> Any:            
        # Respawn dead players if they're still in the game.
        if isinstance(msg, bs.PlayerDiedMessage):
            # Augment standard behavior.
            super().handlemessage(msg)
            player: Player = msg.getplayer(Player)

            player.lives -= 1
            if player.lives < 0:
                logging.exception(
                    "Got lives < 0 in Elim; this shouldn't happen. solo: %s",
                    self._solo_mode,
                )
                player.lives = 0

            # If we have any icons, update their state.
            for icon in player.icons:
                icon.handle_player_died()

            # Play big death sound on our last death
            # or for every one in solo mode.
            if self._solo_mode or player.lives == 0:
                SpazFactory.get().single_player_death_sound.play()

            # If we hit zero lives, we're dead (and our team might be too).
            if player.lives == 0:
                # If the whole team is now dead, mark their survival time.
                if self._get_total_team_lives(player.team) == 0:
                    assert self._start_time is not None
                    
                    player.team.survival_seconds = int(
                        bs.time() - self._start_time
                    )
            else:
                # Otherwise, in regular mode, respawn.
                if not self._solo_mode:
                    self.respawn_player(player)

            # In solo, put ourself at the back of the spawn order.
            if self._solo_mode:
                player.team.spawn_order.remove(player)
                player.team.spawn_order.append(player)

        # Respawn dead pucks.
        elif isinstance(msg, PuckDiedMessage):
            if not self.has_ended():
                bs.timer(2.2, self._spawn_puck)        
        else:
            super().handlemessage(msg)

    def _flash_puck_spawn(self) -> None:
        # Effect >>>>>> Flashly
        bs.emitfx(position=self._puck_spawn_pos, count=int(
            6.0 + 7.0 * 12), scale=1.7, spread=0.4, chunk_type='spark')
        
    def _update(self) -> None:
        if self._solo_mode:
            # For both teams, find the first player on the spawn order
            # list with lives remaining and spawn them if they're not alive.
            for team in self.teams:
                # Prune dead players from the spawn order.
                team.spawn_order = [p for p in team.spawn_order if p]
                for player in team.spawn_order:
                    assert isinstance(player, Player)
                    if player.lives > 0:
                        if not player.is_alive():
                            self.spawn_player(player)
                            self._update_icons()
                        break

        # If we're down to 1 or fewer living teams, start a timer to end
        # the game (allows the dust to settle and draws to occur if deaths
        # are close enough).
        if len(self._get_living_teams()) < 2:
            self._round_end_timer = bs.Timer(0.5, self.end_game)

    def _get_living_teams(self) -> list[Team]:
        return [
            team
            for team in self.teams
            if len(team.players) > 0
            and any(player.lives > 0 for player in team.players)
        ]            

    def _spawn_puck(self) -> None:
        self._swipsound.play()
        self._whistle_sound.play()
        self._flash_puck_spawn()
        assert self._puck_spawn_pos is not None
        self._puck = Puck(position=self._puck_spawn_pos)

    def end_game(self) -> None:
        if self.has_ended():
            return
        results = bs.GameResults()
        self._vs_text = None  # Kill our 'vs' if its there.
        for team in self.teams:
            results.set_team_score(team, team.survival_seconds)
        self.end(results=results)    

class AutoAimer:
    """Automatic item direction for player.

    Args:
        item (bs.Node): The node of the item.
        owner (bs.Node): The node of the player who used the item.
    """

    def __init__(self, item: bs.Node, target: bs.Node | None = None):
        self.item = item
        self.node: bs.Node
        self.target = target

        self.aim_zone: bs.Material = bs.Material()
        

        bs.timer(1, self._move_item)

        # raise the item a little
        self.item.extra_acceleration = (0, 20, 0)
        # if the item exists, then take its position,
        # else "turn the bench"
        if self.item.exists():
            position = self.item.position
        else:
            return

        self.node = bs.newnode('region', attrs={
            'type': 'sphere',
            'position': position,
            'materials': [self.aim_zone]})

        # aiming effect
        bs.animate_array(self.node, 'scale', 3,
                         {0: (0.1, 0.1, 0.1), 1: (60, 60, 60)})

    def _touch_handler(self):
        from bascenev1lib.actor.playerspaz import PlayerSpaz
        node: bs.Node = bs.getcollision().opposingnode
        # Target found! Save it and do something
        self.target = node
        self.node.delete()  # Remove the detection region
        self._move_item()

    def _move_item(self) -> None:
        """The movement of the item to the target."""
        if (self.target and
                self.target.exists() and
                self.item.exists()):
            item_velocity: Sequence[float] = self.item.velocity
            item_position: Sequence[float] = self.item.position
            target_position: Sequence[float] = self.target.position
            self.item.velocity = (
                item_velocity[0] + (target_position[0] - item_position[0]),
                item_velocity[1] + (target_position[1] - item_position[1]),
                item_velocity[2] + (target_position[2] - item_position[2]))

            bs.timer(0.01, self._move_item)

    def off(self) -> None:
        """Deleting a target."""
        self.target = None