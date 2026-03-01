from sprite_object import *

BOOST_DURATION = 5000
BOOST_MULTIPLIER = 0.5


class Weapon(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/weapon/shotgun/0.png', scale=0.4, animation_time=90):
        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time)
        self.images = deque(
            [pg.transform.smoothscale(img, (self.image.get_width() * scale, self.image.get_height() * scale))
             for img in self.images])
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2, HEIGHT - self.images[0].get_height())
        self.reloading = False
        self.num_images = len(self.images)
        self.frame_counter = 0
        self.base_damage = 50
        self.boost_stacks = []

    @property
    def damage(self):
        stacks = len(self.boost_stacks)
        return int(self.base_damage * (1 + stacks * BOOST_MULTIPLIER))

    @property
    def boost_count(self):
        return len(self.boost_stacks)

    @property
    def boost_time_left(self):
        if not self.boost_stacks:
            return 0
        now = pg.time.get_ticks()
        latest = max(self.boost_stacks)
        remaining = latest - now
        return max(0, remaining / 1000)

    def add_boost(self):
        expire = pg.time.get_ticks() + BOOST_DURATION
        self.boost_stacks.append(expire)

    def _update_boosts(self):
        now = pg.time.get_ticks()
        self.boost_stacks = [t for t in self.boost_stacks if t > now]

    def animate_shot(self):
        if self.reloading:
            self.game.player.shot = False
            if self.animation_trigger:
                self.images.rotate(-1)
                self.image = self.images[0]
                self.frame_counter += 1
                if self.frame_counter == self.num_images:
                    self.reloading = False
                    self.frame_counter = 0

    def draw(self):
        self.game.screen.blit(self.images[0], self.weapon_pos)

    def update(self):
        self.check_animation_time()
        self.animate_shot()
        self._update_boosts()