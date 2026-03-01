from sprite_object import *
from sprite_object import DamageBoostPickup
from npc import *
from random import choices, shuffle
import math


class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.pickup_list = []
        self.anim_sprite_path = 'resources/sprites/animated_sprites/'
        self.npc_positions = {}

        self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC]
        self.restricted_area = {(i, j) for i in range(10) for j in range(10)}
        enemies, weights = self.game.score.get_round_config()
        self.enemies = enemies
        self.weights = weights
        self.spawn_npc()
        self._setup_sprites(game)

    def _setup_sprites(self, game):
        add = self.add_sprite
        red = self.anim_sprite_path + 'red_light/0.png'

        add(AnimatedSprite(game))
        add(AnimatedSprite(game, pos=(1.5, 1.5)))
        add(AnimatedSprite(game, pos=(1.5, 7.5)))
        add(AnimatedSprite(game, pos=(5.5, 3.25)))
        add(AnimatedSprite(game, pos=(5.5, 4.75)))
        add(AnimatedSprite(game, pos=(7.5, 2.5)))
        add(AnimatedSprite(game, pos=(7.5, 5.5)))
        add(AnimatedSprite(game, pos=(14.5, 1.5)))
        add(AnimatedSprite(game, pos=(14.5, 4.5)))
        add(AnimatedSprite(game, path=red, pos=(14.5, 5.5)))
        add(AnimatedSprite(game, path=red, pos=(14.5, 7.5)))
        add(AnimatedSprite(game, path=red, pos=(12.5, 7.5)))
        add(AnimatedSprite(game, path=red, pos=(9.5, 7.5)))
        add(AnimatedSprite(game, path=red, pos=(14.5, 12.5)))
        add(AnimatedSprite(game, path=red, pos=(9.5, 20.5)))
        add(AnimatedSprite(game, path=red, pos=(10.5, 20.5)))
        add(AnimatedSprite(game, path=red, pos=(3.5, 14.5)))
        add(AnimatedSprite(game, path=red, pos=(3.5, 18.5)))
        add(AnimatedSprite(game, pos=(14.5, 24.5)))
        add(AnimatedSprite(game, pos=(14.5, 30.5)))
        add(AnimatedSprite(game, pos=(1.5, 30.5)))
        add(AnimatedSprite(game, pos=(1.5, 24.5)))

    def spawn_npc(self):
        valid_tiles = list(self.game.map.reachable_tiles - self.restricted_area)
        shuffle(valid_tiles)

        chosen = set()

        for dist in (4.0, 2.5, 1.5):
            for tile in valid_tiles:
                if len(chosen) >= self.enemies:
                    break
                if tile not in chosen and all(
                    math.hypot(tile[0] - c[0], tile[1] - c[1]) >= dist for c in chosen
                ):
                    chosen.add(tile)
            if len(chosen) >= self.enemies:
                break

        if len(chosen) < self.enemies:
            for tile in valid_tiles:
                if len(chosen) >= self.enemies:
                    break
                if tile not in chosen:
                    chosen.add(tile)

        for x, y in chosen:
            npc_class = choices(self.npc_types, self.weights)[0]
            self.add_npc(npc_class(self.game, pos=(x + 0.5, y + 0.5)))

    def check_win(self):
        if not len(self.npc_positions):
            if self.game.score.is_final_round():
                self.game.complete_game()
            else:
                self.game.object_renderer.win()
                self.game.present()
                pg.time.delay(1500)
                self.game.next_round()

    def spawn_damage_boost(self, pos):
        pickup = DamageBoostPickup(self.game, pos)
        self.pickup_list.append(pickup)

    def remove_pickup(self, pickup):
        if pickup in self.pickup_list:
            self.pickup_list.remove(pickup)

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        [pickup.update() for pickup in self.pickup_list]
        self.check_win()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)
