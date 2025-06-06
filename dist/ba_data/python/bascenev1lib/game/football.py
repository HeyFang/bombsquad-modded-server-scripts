# Released under the MIT License. See LICENSE for details.
#
"""Implements football games (both co-op and teams varieties)."""

# pylint: disable=too-many-lines

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

import math
import random
import logging
from typing import TYPE_CHECKING, override

import bascenev1 as bs

from bascenev1lib.actor.bomb import TNTSpawner
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.actor.respawnicon import RespawnIcon
from bascenev1lib.actor.powerupbox import PowerupBoxFactory, PowerupBox
from bascenev1lib.actor.flag import (
    FlagFactory,
    Flag,
    FlagPickedUpMessage,
    FlagDroppedMessage,
    FlagDiedMessage,
)
from bascenev1lib.actor.spazbot import (
    SpazBotDiedMessage,
    SpazBotPunchedMessage,
    SpazBotSet,
    BrawlerBotLite,
    BrawlerBot,
    BomberBotLite,
    BomberBot,
    TriggerBot,
    ChargerBot,
    TriggerBotPro,
    BrawlerBotPro,
    StickyBot,
    ExplodeyBot,
)

if TYPE_CHECKING:
    from typing import Any, Sequence

    from bascenev1lib.actor.spaz import Spaz
    from bascenev1lib.actor.spazbot import SpazBot


class FootballFlag(Flag):
    """Custom flag class for football games."""

    def __init__(self, position: Sequence[float]):
        super().__init__(
            position=position, dropped_timeout=20, color=(1.0, 1.0, 0.3)
        )
        assert self.node
        self.last_holding_player: bs.Player | None = None
        self.node.is_area_of_interest = True
        self.respawn_timer: bs.Timer | None = None
        self.scored = False
        self.held_count = 0
        self.light = bs.newnode(
            'light',
            owner=self.node,
            attrs={
                'intensity': 0.25,
                'height_attenuated': False,
                'radius': 0.2,
                'color': (0.9, 0.7, 0.0),
            },
        )
        self.node.connectattr('position', self.light, 'position')


class Player(bs.Player['Team']):
    """Our player type for this game."""

    def __init__(self) -> None:
        self.respawn_timer: bs.Timer | None = None
        self.respawn_icon: RespawnIcon | None = None


class Team(bs.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0


# ba_meta export bascenev1.GameActivity
class FootballTeamGame(bs.TeamGameActivity[Player, Team]):
    """Football game for teams mode."""

    name = 'Football'
    description = 'Get the flag to the enemy end zone.'
    available_settings = [
        bs.IntSetting(
            'Score to Win',
            min_value=7,
            default=21,
            increment=7,
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
        bs.BoolSetting('Epic Mode', default=False),
    ]

    @override
    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        # We only support two-team play.
        return issubclass(sessiontype, bs.DualTeamSession)

    @override
    @classmethod
    def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        assert bs.app.classic is not None
        return bs.app.classic.getmaps('football')

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._scoreboard: Scoreboard | None = Scoreboard()

        # Load some media we need.
        self._cheer_sound = bs.getsound('cheer')
        self._chant_sound = bs.getsound('crowdChant')
        self._score_sound = bs.getsound('score')
        self._swipsound = bs.getsound('swip')
        self._whistle_sound = bs.getsound('refWhistle')
        self._score_region_material = bs.Material()
        self._score_region_material.add_actions(
            conditions=('they_have_material', FlagFactory.get().flagmaterial),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', False),
                ('call', 'at_connect', self._handle_score),
            ),
        )
        self._flag_spawn_pos: Sequence[float] | None = None
        self._score_regions: list[bs.NodeActor] = []
        self._flag: FootballFlag | None = None
        self._flag_respawn_timer: bs.Timer | None = None
        self._flag_respawn_light: bs.NodeActor | None = None
        self._score_to_win = int(settings['Score to Win'])
        self._time_limit = float(settings['Time Limit'])
        self._epic_mode = bool(settings['Epic Mode'])
        self.slow_motion = self._epic_mode
        self.default_music = (
            bs.MusicType.EPIC if self._epic_mode else bs.MusicType.FOOTBALL
        )

    @override
    def get_instance_description(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        touchdowns = self._score_to_win / 7

        # NOTE: if use just touchdowns = self._score_to_win // 7
        # and we will need to score, for example, 27 points,
        # we will be required to score 3 (not 4) goals ..
        touchdowns = math.ceil(touchdowns)
        if touchdowns > 1:
            return 'Score ${ARG1} touchdowns.', touchdowns
        return 'Score a touchdown.'

    @override
    def get_instance_description_short(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        touchdowns = self._score_to_win / 7
        touchdowns = math.ceil(touchdowns)
        if touchdowns > 1:
            return 'score ${ARG1} touchdowns', touchdowns
        return 'score a touchdown'

    @override
    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        self.setup_standard_powerup_drops()
        self._flag_spawn_pos = self.map.get_flag_position(None)
        self._spawn_flag()
        defs = self.map.defs
        self._score_regions.append(
            bs.NodeActor(
                bs.newnode(
                    'region',
                    attrs={
                        'position': defs.boxes['goal1'][0:3],
                        'scale': defs.boxes['goal1'][6:9],
                        'type': 'box',
                        'materials': (self._score_region_material,),
                    },
                )
            )
        )
        self._score_regions.append(
            bs.NodeActor(
                bs.newnode(
                    'region',
                    attrs={
                        'position': defs.boxes['goal2'][0:3],
                        'scale': defs.boxes['goal2'][6:9],
                        'type': 'box',
                        'materials': (self._score_region_material,),
                    },
                )
            )
        )
        self._update_scoreboard()
        self._chant_sound.play()

    @override
    def on_team_join(self, team: Team) -> None:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        self._update_scoreboard()

    def _kill_flag(self) -> None:
        self._flag = None

    def _handle_score(self) -> None:
        """A point has been scored."""

        # Our flag might stick around for a second or two
        # make sure it doesn't score again.
        assert self._flag is not None
        if self._flag.scored:
            return
        region = bs.getcollision().sourcenode
        i = None
        for i, score_region in enumerate(self._score_regions):
            if region == score_region.node:
                break
        for team in self.teams:
            if team.id == i:
                team.score += 7

                # Tell all players to celebrate.
                for player in team.players:
                    if player.actor:
                        player.actor.handlemessage(bs.CelebrateMessage(2.0))

                # If someone on this team was last to touch it,
                # give them points.
                assert self._flag is not None
                if (
                    self._flag.last_holding_player
                    and team == self._flag.last_holding_player.team
                ):
                    self.stats.player_scored(
                        self._flag.last_holding_player, 50, big_message=True
                    )
                # End the game if we won.
                if team.score >= self._score_to_win:
                    self.end_game()
        self._score_sound.play()
        self._cheer_sound.play()
        assert self._flag
        self._flag.scored = True

        # Kill the flag (it'll respawn shortly).
        bs.timer(1.0, self._kill_flag)
        light = bs.newnode(
            'light',
            attrs={
                'position': bs.getcollision().position,
                'height_attenuated': False,
                'color': (1, 0, 0),
            },
        )
        bs.animate(light, 'intensity', {0.0: 0, 0.5: 1, 1.0: 0}, loop=True)
        bs.timer(1.0, light.delete)
        bs.cameraflash(duration=10.0)
        self._update_scoreboard()

    @override
    def end_game(self) -> None:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        results = bs.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results, announce_delay=0.8)

    def _update_scoreboard(self) -> None:
        assert self._scoreboard is not None
        for team in self.teams:
            self._scoreboard.set_team_value(
                team, team.score, self._score_to_win
            )

    @override
    def handlemessage(self, msg: Any) -> Any:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        if isinstance(msg, FlagPickedUpMessage):
            assert isinstance(msg.flag, FootballFlag)
            try:
                msg.flag.last_holding_player = msg.node.getdelegate(
                    PlayerSpaz, True
                ).getplayer(Player, True)
            except bs.NotFoundError:
                pass
            msg.flag.held_count += 1

        elif isinstance(msg, FlagDroppedMessage):
            assert isinstance(msg.flag, FootballFlag)
            msg.flag.held_count -= 1

        # Respawn dead players if they're still in the game.
        elif isinstance(msg, bs.PlayerDiedMessage):
            # Augment standard behavior.
            super().handlemessage(msg)
            self.respawn_player(msg.getplayer(Player))

        # Respawn dead flags.
        elif isinstance(msg, FlagDiedMessage):
            if not self.has_ended():
                if msg.self_kill:
                    self._spawn_flag()
                else:
                    self._flag_respawn_timer = bs.Timer(3.0, self._spawn_flag)
                self._flag_respawn_light = bs.NodeActor(
                    bs.newnode(
                        'light',
                        attrs={
                            'position': self._flag_spawn_pos,
                            'height_attenuated': False,
                            'radius': 0.15,
                            'color': (1.0, 1.0, 0.3),
                        },
                    )
                )
                assert self._flag_respawn_light.node
                bs.animate(
                    self._flag_respawn_light.node,
                    'intensity',
                    {0.0: 0, 0.25: 0.15, 0.5: 0},
                    loop=True,
                )
                bs.timer(3.0, self._flag_respawn_light.node.delete)

        else:
            # Augment standard behavior.
            super().handlemessage(msg)

    def _flash_flag_spawn(self) -> None:
        light = bs.newnode(
            'light',
            attrs={
                'position': self._flag_spawn_pos,
                'height_attenuated': False,
                'color': (1, 1, 0),
            },
        )
        bs.animate(light, 'intensity', {0: 0, 0.25: 0.25, 0.5: 0}, loop=True)
        bs.timer(1.0, light.delete)

    def _spawn_flag(self) -> None:
        self._swipsound.play()
        self._whistle_sound.play()
        self._flash_flag_spawn()
        assert self._flag_spawn_pos is not None
        self._flag = FootballFlag(position=self._flag_spawn_pos)


class FootballCoopGame(bs.CoopGameActivity[Player, Team]):
    """Co-op variant of football."""

    name = 'Football'
    tips = ['Use the pick-up button to grab the flag < ${PICKUP} >']
    scoreconfig = bs.ScoreConfig(
        scoretype=bs.ScoreType.MILLISECONDS, version='B'
    )

    default_music = bs.MusicType.FOOTBALL

    # FIXME: Need to update co-op games to use getscoreconfig.
    @override
    def get_score_type(self) -> str:
        return 'time'

    @override
    def get_instance_description(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        touchdowns = self._score_to_win / 7
        touchdowns = math.ceil(touchdowns)
        if touchdowns > 1:
            return 'Score ${ARG1} touchdowns.', touchdowns
        return 'Score a touchdown.'

    @override
    def get_instance_description_short(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        touchdowns = self._score_to_win / 7
        touchdowns = math.ceil(touchdowns)
        if touchdowns > 1:
            return 'score ${ARG1} touchdowns', touchdowns
        return 'score a touchdown'

    def __init__(self, settings: dict):
        settings['map'] = 'Football Stadium'
        super().__init__(settings)
        self._preset = settings.get('preset', 'rookie')

        # Load some media we need.
        self._cheer_sound = bs.getsound('cheer')
        self._boo_sound = bs.getsound('boo')
        self._chant_sound = bs.getsound('crowdChant')
        self._score_sound = bs.getsound('score')
        self._swipsound = bs.getsound('swip')
        self._whistle_sound = bs.getsound('refWhistle')
        self._score_to_win = 21
        self._score_region_material = bs.Material()
        self._score_region_material.add_actions(
            conditions=('they_have_material', FlagFactory.get().flagmaterial),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', False),
                ('call', 'at_connect', self._handle_score),
            ),
        )
        self._powerup_center = (0, 2, 0)
        self._powerup_spread = (10, 5.5)
        self._player_has_dropped_bomb = False
        self._player_has_punched = False
        self._scoreboard: Scoreboard | None = None
        self._flag_spawn_pos: Sequence[float] | None = None
        self._score_regions: list[bs.NodeActor] = []
        self._exclude_powerups: list[str] = []
        self._have_tnt = False
        self._bot_types_initial: list[type[SpazBot]] | None = None
        self._bot_types_7: list[type[SpazBot]] | None = None
        self._bot_types_14: list[type[SpazBot]] | None = None
        self._bot_team: Team | None = None
        self._starttime_ms: int | None = None
        self._time_text: bs.NodeActor | None = None
        self._time_text_input: bs.NodeActor | None = None
        self._tntspawner: TNTSpawner | None = None
        self._bots = SpazBotSet()
        self._bot_spawn_timer: bs.Timer | None = None
        self._powerup_drop_timer: bs.Timer | None = None
        self._scoring_team: Team | None = None
        self._final_time_ms: int | None = None
        self._time_text_timer: bs.Timer | None = None
        self._flag_respawn_light: bs.Actor | None = None
        self._flag: FootballFlag | None = None

    @override
    def on_transition_in(self) -> None:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        super().on_transition_in()
        self._scoreboard = Scoreboard()
        self._flag_spawn_pos = self.map.get_flag_position(None)
        self._spawn_flag()

        # Set up the two score regions.
        defs = self.map.defs
        self._score_regions.append(
            bs.NodeActor(
                bs.newnode(
                    'region',
                    attrs={
                        'position': defs.boxes['goal1'][0:3],
                        'scale': defs.boxes['goal1'][6:9],
                        'type': 'box',
                        'materials': [self._score_region_material],
                    },
                )
            )
        )
        self._score_regions.append(
            bs.NodeActor(
                bs.newnode(
                    'region',
                    attrs={
                        'position': defs.boxes['goal2'][0:3],
                        'scale': defs.boxes['goal2'][6:9],
                        'type': 'box',
                        'materials': [self._score_region_material],
                    },
                )
            )
        )
        self._chant_sound.play()

    @override
    def on_begin(self) -> None:
        # FIXME: Split this up a bit.
        # pylint: disable=too-many-statements
        from bascenev1lib.actor import controlsguide

        super().on_begin()

        # Show controls help in demo or arcade mode.
        if bs.app.env.demo or bs.app.env.arcade:
            controlsguide.ControlsGuide(
                delay=3.0, lifespan=10.0, bright=True
            ).autoretain()
        assert self.initialplayerinfos is not None
        abot: type[SpazBot]
        bbot: type[SpazBot]
        cbot: type[SpazBot]
        if self._preset in ['rookie', 'rookie_easy']:
            self._exclude_powerups = ['curse']
            self._have_tnt = False
            abot = (
                BrawlerBotLite if self._preset == 'rookie_easy' else BrawlerBot
            )
            self._bot_types_initial = [abot] * len(self.initialplayerinfos)
            bbot = BomberBotLite if self._preset == 'rookie_easy' else BomberBot
            self._bot_types_7 = [bbot] * (
                1 if len(self.initialplayerinfos) < 3 else 2
            )
            cbot = BomberBot if self._preset == 'rookie_easy' else TriggerBot
            self._bot_types_14 = [cbot] * (
                1 if len(self.initialplayerinfos) < 3 else 2
            )
        elif self._preset == 'tournament':
            self._exclude_powerups = []
            self._have_tnt = True
            self._bot_types_initial = [BrawlerBot] * (
                1 if len(self.initialplayerinfos) < 2 else 2
            )
            self._bot_types_7 = [TriggerBot] * (
                1 if len(self.initialplayerinfos) < 3 else 2
            )
            self._bot_types_14 = [ChargerBot] * (
                1 if len(self.initialplayerinfos) < 4 else 2
            )
        elif self._preset in ['pro', 'pro_easy', 'tournament_pro']:
            self._exclude_powerups = ['curse']
            self._have_tnt = True
            self._bot_types_initial = [ChargerBot] * len(
                self.initialplayerinfos
            )
            abot = BrawlerBot if self._preset == 'pro' else BrawlerBotLite
            typed_bot_list: list[type[SpazBot]] = []
            self._bot_types_7 = (
                typed_bot_list
                + [abot]
                + [BomberBot] * (1 if len(self.initialplayerinfos) < 3 else 2)
            )
            bbot = TriggerBotPro if self._preset == 'pro' else TriggerBot
            self._bot_types_14 = [bbot] * (
                1 if len(self.initialplayerinfos) < 3 else 2
            )
        elif self._preset in ['uber', 'uber_easy']:
            self._exclude_powerups = []
            self._have_tnt = True
            abot = BrawlerBotPro if self._preset == 'uber' else BrawlerBot
            bbot = TriggerBotPro if self._preset == 'uber' else TriggerBot
            typed_bot_list_2: list[type[SpazBot]] = []
            self._bot_types_initial = (
                typed_bot_list_2
                + [StickyBot]
                + [abot] * len(self.initialplayerinfos)
            )
            self._bot_types_7 = [bbot] * (
                1 if len(self.initialplayerinfos) < 3 else 2
            )
            self._bot_types_14 = [ExplodeyBot] * (
                1 if len(self.initialplayerinfos) < 3 else 2
            )
        else:
            raise RuntimeError()

        self.setup_low_life_warning_sound()

        self._drop_powerups(standard_points=True)
        bs.timer(4.0, self._start_powerup_drops)

        # Make a bogus team for our bots.
        bad_team_name = self.get_team_display_string('Bad Guys')
        self._bot_team = Team()
        self._bot_team.manual_init(
            team_id=1, name=bad_team_name, color=(0.5, 0.4, 0.4)
        )

        for team in [self.teams[0], self._bot_team]:
            team.score = 0

        self.update_scores()

        # Time display.
        starttime_ms = int(bs.time() * 1000.0)
        assert isinstance(starttime_ms, int)
        self._starttime_ms = starttime_ms
        self._time_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'v_attach': 'top',
                    'h_attach': 'center',
                    'h_align': 'center',
                    'color': (1, 1, 0.5, 1),
                    'flatness': 0.5,
                    'shadow': 0.5,
                    'position': (0, -50),
                    'scale': 1.3,
                    'text': '',
                },
            )
        )
        self._time_text_input = bs.NodeActor(
            bs.newnode('timedisplay', attrs={'showsubseconds': True})
        )
        self.globalsnode.connectattr(
            'time', self._time_text_input.node, 'time2'
        )
        assert self._time_text_input.node
        assert self._time_text.node
        self._time_text_input.node.connectattr(
            'output', self._time_text.node, 'text'
        )

        # Our TNT spawner (if applicable).
        if self._have_tnt:
            self._tntspawner = TNTSpawner(position=(0, 1, -1))

        self._bots = SpazBotSet()
        self._bot_spawn_timer = bs.Timer(1.0, self._update_bots, repeat=True)

        for bottype in self._bot_types_initial:
            self._spawn_bot(bottype)

    def _on_bot_spawn(self, spaz: SpazBot) -> None:
        # We want to move to the left by default.
        spaz.target_point_default = bs.Vec3(0, 0, 0)

    def _spawn_bot(
        self, spaz_type: type[SpazBot], immediate: bool = False
    ) -> None:
        assert self._bot_team is not None
        pos = self.map.get_start_position(self._bot_team.id)
        self._bots.spawn_bot(
            spaz_type,
            pos=pos,
            spawn_time=0.001 if immediate else 3.0,
            on_spawn_call=self._on_bot_spawn,
        )

    def _update_bots(self) -> None:
        bots = self._bots.get_living_bots()
        for bot in bots:
            bot.target_flag = None

        # If we've got a flag and no player are holding it, find the closest
        # bot to it, and make them the designated flag-bearer.
        assert self._flag is not None
        if self._flag.node:
            for player in self.players:
                if player.actor:
                    assert isinstance(player.actor, PlayerSpaz)
                    if (
                        player.actor.is_alive()
                        and player.actor.node.hold_node == self._flag.node
                    ):
                        return

            flagpos = bs.Vec3(self._flag.node.position)
            closest_bot: SpazBot | None = None
            closest_dist = 0.0  # Always gets assigned first time through.
            for bot in bots:
                # If a bot is picked up, he should forget about the flag.
                if bot.held_count > 0:
                    continue
                assert bot.node
                botpos = bs.Vec3(bot.node.position)
                botdist = (botpos - flagpos).length()
                if closest_bot is None or botdist < closest_dist:
                    closest_bot = bot
                    closest_dist = botdist
            if closest_bot is not None:
                closest_bot.target_flag = self._flag

    def _drop_powerup(self, index: int, poweruptype: str | None = None) -> None:
        if poweruptype is None:
            poweruptype = PowerupBoxFactory.get().get_random_powerup_type(
                excludetypes=self._exclude_powerups
            )
        PowerupBox(
            position=self.map.powerup_spawn_points[index],
            poweruptype=poweruptype,
        ).autoretain()

    def _start_powerup_drops(self) -> None:
        self._powerup_drop_timer = bs.Timer(
            3.0, self._drop_powerups, repeat=True
        )

    def _drop_powerups(
        self, standard_points: bool = False, poweruptype: str | None = None
    ) -> None:
        """Generic powerup drop."""
        if standard_points:
            spawnpoints = self.map.powerup_spawn_points
            for i, _point in enumerate(spawnpoints):
                bs.timer(
                    1.0 + i * 0.5, bs.Call(self._drop_powerup, i, poweruptype)
                )
        else:
            point = (
                self._powerup_center[0]
                + random.uniform(
                    -1.0 * self._powerup_spread[0],
                    1.0 * self._powerup_spread[0],
                ),
                self._powerup_center[1],
                self._powerup_center[2]
                + random.uniform(
                    -self._powerup_spread[1], self._powerup_spread[1]
                ),
            )

            # Drop one random one somewhere.
            PowerupBox(
                position=point,
                poweruptype=PowerupBoxFactory.get().get_random_powerup_type(
                    excludetypes=self._exclude_powerups
                ),
            ).autoretain()

    def _kill_flag(self) -> None:
        try:
            assert self._flag is not None
            self._flag.handlemessage(bs.DieMessage())
        except Exception:
            logging.exception('Error in _kill_flag.')

    def _handle_score(self) -> None:
        """a point has been scored"""
        # FIXME tidy this up
        # pylint: disable=too-many-branches

        # Our flag might stick around for a second or two;
        # we don't want it to be able to score again.
        assert self._flag is not None
        if self._flag.scored:
            return

        # See which score region it was.
        region = bs.getcollision().sourcenode
        i = None
        for i, score_region in enumerate(self._score_regions):
            if region == score_region.node:
                break

        for team in [self.teams[0], self._bot_team]:
            assert team is not None
            if team.id == i:
                team.score += 7

                # Tell all players (or bots) to celebrate.
                if i == 0:
                    for player in team.players:
                        if player.actor:
                            player.actor.handlemessage(bs.CelebrateMessage(2.0))
                else:
                    self._bots.celebrate(2.0)

        # If the good guys scored, add more enemies.
        if i == 0:
            if self.teams[0].score == 7:
                assert self._bot_types_7 is not None
                for bottype in self._bot_types_7:
                    self._spawn_bot(bottype)
            elif self.teams[0].score == 14:
                assert self._bot_types_14 is not None
                for bottype in self._bot_types_14:
                    self._spawn_bot(bottype)

        self._score_sound.play()
        if i == 0:
            self._cheer_sound.play()
        else:
            self._boo_sound.play()

        # Kill the flag (it'll respawn shortly).
        self._flag.scored = True

        bs.timer(0.2, self._kill_flag)

        self.update_scores()
        light = bs.newnode(
            'light',
            attrs={
                'position': bs.getcollision().position,
                'height_attenuated': False,
                'color': (1, 0, 0),
            },
        )
        bs.animate(light, 'intensity', {0: 0, 0.5: 1, 1.0: 0}, loop=True)
        bs.timer(1.0, light.delete)
        if i == 0:
            bs.cameraflash(duration=10.0)

    @override
    def end_game(self) -> None:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        bs.setmusic(None)
        self._bots.final_celebrate()
        bs.timer(0.001, bs.Call(self.do_end, 'defeat'))

    def update_scores(self) -> None:
        """update scoreboard and check for winners"""
        # FIXME: tidy this up
        # pylint: disable=too-many-nested-blocks
        have_scoring_team = False
        win_score = self._score_to_win
        for team in [self.teams[0], self._bot_team]:
            assert team is not None
            assert self._scoreboard is not None
            self._scoreboard.set_team_value(team, team.score, win_score)
            if team.score >= win_score:
                if not have_scoring_team:
                    self._scoring_team = team
                    if team is self._bot_team:
                        self.end_game()
                    else:
                        bs.setmusic(bs.MusicType.VICTORY)

                        # Completion achievements.
                        assert self._bot_team is not None
                        if self._preset in ['rookie', 'rookie_easy']:
                            self._award_achievement(
                                'Rookie Football Victory', sound=False
                            )
                            if self._bot_team.score == 0:
                                self._award_achievement(
                                    'Rookie Football Shutout', sound=False
                                )
                        elif self._preset in ['pro', 'pro_easy']:
                            self._award_achievement(
                                'Pro Football Victory', sound=False
                            )
                            if self._bot_team.score == 0:
                                self._award_achievement(
                                    'Pro Football Shutout', sound=False
                                )
                        elif self._preset in ['uber', 'uber_easy']:
                            self._award_achievement(
                                'Uber Football Victory', sound=False
                            )
                            if self._bot_team.score == 0:
                                self._award_achievement(
                                    'Uber Football Shutout', sound=False
                                )
                            if (
                                not self._player_has_dropped_bomb
                                and not self._player_has_punched
                            ):
                                self._award_achievement(
                                    'Got the Moves', sound=False
                                )
                        self._bots.stop_moving()
                        self.show_zoom_message(
                            bs.Lstr(resource='victoryText'),
                            scale=1.0,
                            duration=4.0,
                        )
                        self.celebrate(10.0)
                        assert self._starttime_ms is not None
                        self._final_time_ms = int(
                            int(bs.time() * 1000.0) - self._starttime_ms
                        )
                        self._time_text_timer = None
                        assert (
                            self._time_text_input is not None
                            and self._time_text_input.node
                        )
                        self._time_text_input.node.timemax = self._final_time_ms

                        self.do_end('victory')

    def do_end(self, outcome: str) -> None:
        """End the game with the specified outcome."""
        if outcome == 'defeat':
            self.fade_to_red()
        assert self._final_time_ms is not None
        scoreval = (
            None if outcome == 'defeat' else int(self._final_time_ms // 10)
        )
        self.end(
            delay=3.0,
            results={
                'outcome': outcome,
                'score': scoreval,
                'score_order': 'decreasing',
                'playerinfos': self.initialplayerinfos,
            },
        )

    @override
    def handlemessage(self, msg: Any) -> Any:
        """handle high-level game messages"""
        if isinstance(msg, bs.PlayerDiedMessage):
            # Augment standard behavior.
            super().handlemessage(msg)

            # Respawn them shortly.
            player = msg.getplayer(Player)
            assert self.initialplayerinfos is not None
            respawn_time = 2.0 + len(self.initialplayerinfos) * 1.0
            player.respawn_timer = bs.Timer(
                respawn_time, bs.Call(self.spawn_player_if_exists, player)
            )
            player.respawn_icon = RespawnIcon(player, respawn_time)

        elif isinstance(msg, SpazBotDiedMessage):
            # Every time a bad guy dies, spawn a new one.
            bs.timer(3.0, bs.Call(self._spawn_bot, (type(msg.spazbot))))

        elif isinstance(msg, SpazBotPunchedMessage):
            if self._preset in ['rookie', 'rookie_easy']:
                if msg.damage >= 500:
                    self._award_achievement('Super Punch')
            elif self._preset in ['pro', 'pro_easy']:
                if msg.damage >= 1000:
                    self._award_achievement('Super Mega Punch')

        # Respawn dead flags.
        elif isinstance(msg, FlagDiedMessage):
            assert isinstance(msg.flag, FootballFlag)
            if msg.self_kill:
                self._spawn_flag()
            else:
                msg.flag.respawn_timer = bs.Timer(3.0, self._spawn_flag)
            self._flag_respawn_light = bs.NodeActor(
                bs.newnode(
                    'light',
                    attrs={
                        'position': self._flag_spawn_pos,
                        'height_attenuated': False,
                        'radius': 0.15,
                        'color': (1.0, 1.0, 0.3),
                    },
                )
            )
            assert self._flag_respawn_light.node
            bs.animate(
                self._flag_respawn_light.node,
                'intensity',
                {0: 0, 0.25: 0.15, 0.5: 0},
                loop=(not msg.self_kill),
            )
            bs.timer(3.0, self._flag_respawn_light.node.delete)
        else:
            return super().handlemessage(msg)
        return None

    def _handle_player_dropped_bomb(self, player: Spaz, bomb: bs.Actor) -> None:
        del player, bomb  # Unused.
        self._player_has_dropped_bomb = True

    def _handle_player_punched(self, player: Spaz) -> None:
        del player  # Unused.
        self._player_has_punched = True

    @override
    def spawn_player(self, player: Player) -> bs.Actor:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        spaz = self.spawn_player_spaz(
            player, position=self.map.get_start_position(player.team.id)
        )
        if self._preset in ['rookie_easy', 'pro_easy', 'uber_easy']:
            spaz.impact_scale = 0.25
        spaz.add_dropped_bomb_callback(self._handle_player_dropped_bomb)
        spaz.punch_callback = self._handle_player_punched
        return spaz

    def _flash_flag_spawn(self) -> None:
        light = bs.newnode(
            'light',
            attrs={
                'position': self._flag_spawn_pos,
                'height_attenuated': False,
                'color': (1, 1, 0),
            },
        )
        bs.animate(light, 'intensity', {0: 0, 0.25: 0.25, 0.5: 0}, loop=True)
        bs.timer(1.0, light.delete)

    def _spawn_flag(self) -> None:
        self._swipsound.play()
        self._whistle_sound.play()
        self._flash_flag_spawn()
        assert self._flag_spawn_pos is not None
        self._flag = FootballFlag(position=self._flag_spawn_pos)
