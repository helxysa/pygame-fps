import pygame as pg
from settings import *


class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture('resources/textures/sky.png', (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0
        self.blood_screen = self.get_texture('resources/textures/blood_screen.png', RES)
        self.digit_size = 40
        self.digit_images = [self.get_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))
        self.hud_font = pg.font.Font('resources/fonts/PressStart2P.ttf', 12)
        self.game_over_image = self.get_texture('resources/textures/game_over.png', RES)
        self.win_image = self.get_texture('resources/textures/win.png', RES)

    def draw(self):
        self.draw_background()
        self.render_game_objects()
        self.draw_hud()

    def win(self):
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))

    def draw_hud(self):
        health = str(self.game.player.health)
        hp_label = self.hud_font.render('HP', True, (180, 30, 30))
        self.screen.blit(hp_label, (10, 12))
        offset_x = 42
        for i, char in enumerate(health):
            self.screen.blit(self.digits[char], (offset_x + i * self.digit_size, 5))
        self.screen.blit(self.digits['10'], (offset_x + (i + 1) * self.digit_size, 5))

        score = self.game.score
        round_text = self.hud_font.render(f'ROUND {score.current_round}', True, (220, 50, 50))
        round_rect = round_text.get_rect(midtop=(HALF_WIDTH, 10))
        self.screen.blit(round_text, round_rect)

        kills_text = self.hud_font.render(f'KILLS: {score.kills}', True, (220, 220, 220))
        kills_rect = kills_text.get_rect(midtop=(HALF_WIDTH, 30))
        self.screen.blit(kills_text, kills_rect)

        lives_x = WIDTH - 10
        for v in range(score.lives):
            pg.draw.rect(self.screen, (180, 30, 30), (lives_x - (v + 1) * 28, 10, 22, 22))
            cross = self.hud_font.render('+', True, (255, 255, 255))
            cross_rect = cross.get_rect(center=(lives_x - (v + 1) * 28 + 11, 21))
            self.screen.blit(cross, cross_rect)

        weapon = self.game.weapon
        if weapon.boost_count > 0:
            self._draw_boost_hud(weapon)

    def _draw_boost_hud(self, weapon):
        stacks = weapon.boost_count
        time_left = weapon.boost_time_left
        dmg = weapon.damage

        box_w, box_h = 180, 48
        box_x = HALF_WIDTH - box_w // 2
        box_y = HEIGHT - 70
        box_surf = pg.Surface((box_w, box_h), pg.SRCALPHA)
        box_surf.fill((0, 0, 0, 140))
        pg.draw.rect(box_surf, (255, 80, 20), (0, 0, box_w, box_h), 1)
        self.screen.blit(box_surf, (box_x, box_y))

        mult_text = self.hud_font.render(f'DMG x{1 + stacks * 0.5:.1f}', True, (255, 160, 40))
        mult_rect = mult_text.get_rect(center=(HALF_WIDTH, box_y + 14))
        self.screen.blit(mult_text, mult_rect)

        bar_w = box_w - 20
        bar_h = 6
        bar_x = box_x + 10
        bar_y = box_y + 30
        pg.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h))
        fill = min(1.0, time_left / 5.0)
        fill_color = (255, 160, 40) if time_left > 2 else (255, 60, 20)
        pg.draw.rect(self.screen, fill_color, (bar_x, bar_y, int(bar_w * fill), bar_h))

        time_text = self.hud_font.render(f'{time_left:.1f}s', True, (200, 200, 200))
        time_rect = time_text.get_rect(center=(HALF_WIDTH, box_y + 43))
        self.screen.blit(time_text, time_rect)

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0, 0))

    def draw_background(self):
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        return {
            1: self.get_texture('resources/textures/1.png'),
            2: self.get_texture('resources/textures/2.png'),
            3: self.get_texture('resources/textures/3.png'),
            4: self.get_texture('resources/textures/4.png'),
            5: self.get_texture('resources/textures/5.png'),
        }
