import pygame as pg
import sys
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *
from score import ScoreManager


class Game:
    def __init__(self):
        pg.init()
        import os
        info = pg.display.Info()
        os.environ['SDL_VIDEO_WINDOW_POS'] = f'{(info.current_w - WIN_WIDTH) // 2},{(info.current_h - WIN_HEIGHT) // 2}'
        self.window = pg.display.set_mode(WIN_RES, pg.NOFRAME)
        self.screen = pg.Surface(RES)
        pg.display.set_caption('Project Hellbreaker')
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)

        self.others_path = 'resources/sprites/others/'
        zoom = 1.15
        zoomed_size = (int(WIDTH * zoom), int(HEIGHT * zoom))
        self.init_image = self.load_image(self.others_path + 'init.png', zoomed_size)
        self.loading_image = self.load_image(self.others_path + 'laoding.png', zoomed_size)
        self.dead_image = self.load_image(self.others_path + 'dead.png', zoomed_size)
        offset_x = (zoomed_size[0] - WIDTH) // 2
        offset_y = (zoomed_size[1] - HEIGHT) // 2
        self.img_offset = (-offset_x, -offset_y)

        font_path = 'resources/fonts/PressStart2P.ttf'
        self.font_title = pg.font.Font(font_path, 36)
        self.font_option = pg.font.Font(font_path, 28)
        self.font_medium = pg.font.Font(font_path, 18)
        self.font_hint = pg.font.Font(font_path, 12)
        self.font_small = pg.font.Font(font_path, 10)
        self.font_section = pg.font.Font(font_path, 14)

        self.score = ScoreManager()
        self.player_name = ''
        self.max_name_len = 8

        self.state = 'menu'
        self.menu_selected = 0
        self.menu_options = ['PLAY', 'INSTRUCOES', 'RANKING']
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)

    @staticmethod
    def load_image(path, res):
        img = pg.image.load(path).convert_alpha()
        return pg.transform.scale(img, res)

    def present(self):
        scaled = pg.transform.scale(self.screen, WIN_RES)
        self.window.blit(scaled, (0, 0))
        pg.display.flip()

    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        pg.mixer.music.play(-1)

    def start_game(self):
        self.score.reset()
        self._enter_round_intro()

    def next_round(self):
        self.score.next_round()
        self._enter_round_intro()

    def continue_game(self):
        self._enter_round_intro()

    def complete_game(self):
        pg.mixer.music.stop()
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        pg.event.clear()
        self.player_name = ''
        self.state = 'victory'

    def _enter_round_intro(self):
        self.screen.blit(self.loading_image, self.img_offset)
        self.present()
        self.new_game()
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        self.round_intro_start = pg.time.get_ticks()
        self.state = 'round_intro'

    def go_to_menu(self):
        pg.mixer.music.stop()
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        self.state = 'menu'
        self.menu_selected = 0

    def go_to_dead(self):
        pg.mixer.music.stop()
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        pg.event.clear()
        has_lives = self.score.lose_life()
        if has_lives:
            self.state = 'dead'
        else:
            self.player_name = ''
            self.state = 'game_over'

    def update(self):
        self.player.update()
        if self.state != 'playing':
            return
        self.raycasting.update()
        self.object_handler.update()
        if self.state != 'playing':
            return
        self.weapon.update()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'Project Hellbreaker - {self.clock.get_fps():.1f} FPS')

    def draw(self):
        if self.state != 'playing':
            return
        self.object_renderer.draw()
        self.weapon.draw()
        self.present()

    def draw_menu(self):
        self.screen.blit(self.init_image, self.img_offset)

        overlay = pg.Surface(RES, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))

        for i, option in enumerate(self.menu_options):
            y_pos = HEIGHT // 2 + 60 + i * 60

            if i == self.menu_selected:
                text = self.font_option.render(f'> {option} <', True, (220, 50, 50))
            else:
                shadow = self.font_option.render(option, True, (0, 0, 0))
                shadow_rect = shadow.get_rect(center=(HALF_WIDTH + 2, y_pos + 2))
                self.screen.blit(shadow, shadow_rect)
                text = self.font_option.render(option, True, (190, 190, 190))

            text_rect = text.get_rect(center=(HALF_WIDTH, y_pos))
            self.screen.blit(text, text_rect)

        hint = self.font_hint.render('[W/S] Navegar  [ENTER] Selecionar', True, (150, 150, 150))
        hint_rect = hint.get_rect(center=(HALF_WIDTH, HEIGHT - 35))
        self.screen.blit(hint, hint_rect)

        self.present()
        self.clock.tick(60)

    def draw_instructions(self):
        self.screen.blit(self.init_image, self.img_offset)

        overlay = pg.Surface(RES, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font_option.render('INSTRUCOES', True, (220, 50, 50))
        title_rect = title.get_rect(center=(HALF_WIDTH, 60))
        self.screen.blit(title, title_rect)

        pg.draw.line(self.screen, (120, 30, 30), (HALF_WIDTH - 140, 90), (HALF_WIDTH + 140, 90), 2)

        instructions = [
            ('MOVIMENTO', [
                'W/A/S/D  -  Mover',
                'Mouse  -  Olhar ao redor',
            ]),
            ('COMBATE', [
                'Botao esquerdo  -  Atirar',
                'Mate o maximo de inimigos!',
            ]),
            ('SISTEMA', [
                'Sao 10 rounds, cada vez mais dificeis',
                'Voce tem 3 vidas por partida',
                'Kills acumulam entre os rounds',
                'ESC  -  Voltar ao menu',
            ]),
        ]

        y = 120
        for section_title, lines in instructions:
            section = self.font_section.render(section_title, True, (200, 60, 60))
            self.screen.blit(section, (HALF_WIDTH - 250, y))
            y += 35
            for line in lines:
                text = self.font_small.render(line, True, (190, 190, 190))
                self.screen.blit(text, (HALF_WIDTH - 220, y))
                y += 26
            y += 14

        hint = self.font_hint.render('[ESC] Voltar', True, (150, 150, 150))
        hint_rect = hint.get_rect(center=(HALF_WIDTH, HEIGHT - 35))
        self.screen.blit(hint, hint_rect)

        self.present()
        self.clock.tick(60)

    def draw_round_intro(self):
        from score import MAX_ROUNDS
        round_num = self.score.current_round
        elapsed = pg.time.get_ticks() - self.round_intro_start

        self.screen.blit(self.init_image, self.img_offset)

        overlay = pg.Surface(RES, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        r_color = (min(220, 80 + round_num * 15), max(20, 50 - round_num * 3), max(20, 50 - round_num * 3))
        cy = HALF_HEIGHT - 30

        line_w = min(420, int(elapsed * 0.8))
        pg.draw.line(self.screen, r_color,
                     (HALF_WIDTH - line_w // 2, cy - 30),
                     (HALF_WIDTH + line_w // 2, cy - 30), 2)

        if elapsed > 200:
            shadow = self.font_title.render(f'ROUND {round_num}', True, (0, 0, 0))
            self.screen.blit(shadow, shadow.get_rect(center=(HALF_WIDTH + 3, cy + 3)))
            title = self.font_title.render(f'ROUND {round_num}', True, r_color)
            self.screen.blit(title, title.get_rect(center=(HALF_WIDTH, cy)))

        if elapsed > 400:
            desc = self.score.get_round_description()
            desc_text = self.font_section.render(desc.upper(), True, (200, 200, 200))
            self.screen.blit(desc_text, desc_text.get_rect(center=(HALF_WIDTH, cy + 38)))

        pg.draw.line(self.screen, r_color,
                     (HALF_WIDTH - line_w // 2, cy + 60),
                     (HALF_WIDTH + line_w // 2, cy + 60), 2)

        if elapsed > 600:
            enemies, _ = self.score.get_round_config()
            enemy_names = self.score.get_round_enemy_names()
            dot_colors = [(180, 180, 180), (200, 100, 50), (150, 50, 200)]

            info_y = cy + 90
            enemies_label = self.font_hint.render(f'{enemies} INIMIGOS', True, (220, 220, 220))
            self.screen.blit(enemies_label, enemies_label.get_rect(center=(HALF_WIDTH, info_y)))

            total_names_w = sum(self.font_small.size(n)[0] + 24 for n in enemy_names) - 10
            name_x = HALF_WIDTH - total_names_w // 2
            for j, name in enumerate(enemy_names):
                pg.draw.circle(self.screen, dot_colors[j], (name_x + 4, info_y + 30), 4)
                name_surf = self.font_small.render(name, True, (170, 170, 170))
                self.screen.blit(name_surf, (name_x + 14, info_y + 24))
                name_x += name_surf.get_width() + 24

        if elapsed > 700:
            bar_w_px, bar_h_px = 300, 6
            bar_x = HALF_WIDTH - bar_w_px // 2
            bar_y = cy + 165
            pg.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_w_px, bar_h_px))
            fill_w = int(bar_w_px * round_num / MAX_ROUNDS)
            pg.draw.rect(self.screen, r_color, (bar_x, bar_y, fill_w, bar_h_px))
            progress = self.font_small.render(f'{round_num} / {MAX_ROUNDS}', True, (120, 120, 120))
            self.screen.blit(progress, progress.get_rect(center=(HALF_WIDTH, bar_y + 18)))

            kills_stat = self.font_small.render(f'KILLS: {self.score.kills}', True, (180, 180, 180))
            lives_stat = self.font_small.render(f'VIDAS: {self.score.lives}', True, (180, 80, 80))
            stats_w = kills_stat.get_width() + 40 + lives_stat.get_width()
            stats_x = HALF_WIDTH - stats_w // 2
            stats_y = bar_y + 40
            self.screen.blit(kills_stat, (stats_x, stats_y))
            self.screen.blit(lives_stat, (stats_x + kills_stat.get_width() + 40, stats_y))

        if elapsed > 1000:
            if (elapsed // 500) % 2 == 0:
                hint = self.font_hint.render('Pressione qualquer tecla', True, (180, 180, 180))
                self.screen.blit(hint, hint.get_rect(center=(HALF_WIDTH, HEIGHT - 45)))

        self.present()
        self.clock.tick(60)

    def draw_victory(self):
        self.screen.fill((0, 0, 0))

        overlay = pg.Surface(RES, pg.SRCALPHA)
        overlay.fill((10, 30, 10, 200))
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render('VITORIA!', True, (50, 220, 50))
        title_rect = title.get_rect(center=(HALF_WIDTH, HEIGHT // 4))
        self.screen.blit(title, title_rect)

        sub = self.font_medium.render('Todos os rounds completos!', True, (200, 200, 200))
        sub_rect = sub.get_rect(center=(HALF_WIDTH, HEIGHT // 4 + 50))
        self.screen.blit(sub, sub_rect)

        kills = self.font_option.render(f'{self.score.kills}', True, (255, 255, 255))
        kills_rect = kills.get_rect(center=(HALF_WIDTH, HEIGHT // 2))
        self.screen.blit(kills, kills_rect)

        kills_label = self.font_hint.render('KILLS TOTAIS', True, (160, 160, 160))
        kills_label_rect = kills_label.get_rect(center=(HALF_WIDTH, HEIGHT // 2 + 35))
        self.screen.blit(kills_label, kills_label_rect)

        prompt = self.font_section.render('DIGITE SEU NOME:', True, (200, 200, 200))
        prompt_rect = prompt.get_rect(center=(HALF_WIDTH, HEIGHT // 2 + 80))
        self.screen.blit(prompt, prompt_rect)

        display_name = self.player_name + '_'
        name_text = self.font_option.render(display_name, True, (50, 220, 50))
        name_rect = name_text.get_rect(center=(HALF_WIDTH, HEIGHT // 2 + 125))
        self.screen.blit(name_text, name_rect)

        if len(self.player_name) > 0:
            save_hint = self.font_hint.render('[ENTER] Salvar', True, (190, 190, 190))
            save_rect = save_hint.get_rect(center=(HALF_WIDTH, HEIGHT - 80))
            self.screen.blit(save_hint, save_rect)

        skip = self.font_hint.render('[ESC] Pular', True, (120, 120, 120))
        skip_rect = skip.get_rect(center=(HALF_WIDTH, HEIGHT - 50))
        self.screen.blit(skip, skip_rect)

        self.present()
        self.clock.tick(60)

    def draw_dead(self):
        self.screen.blit(self.dead_image, self.img_offset)

        overlay = pg.Surface(RES, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render('VOCE MORREU', True, (220, 30, 30))
        title_rect = title.get_rect(center=(HALF_WIDTH, HEIGHT // 3))
        self.screen.blit(title, title_rect)

        round_text = self.font_medium.render(f'ROUND {self.score.current_round}', True, (220, 160, 50))
        round_rect = round_text.get_rect(center=(HALF_WIDTH, HEIGHT // 2 - 40))
        self.screen.blit(round_text, round_rect)

        kills = self.font_medium.render(f'KILLS: {self.score.kills}', True, (220, 220, 220))
        kills_rect = kills.get_rect(center=(HALF_WIDTH, HEIGHT // 2))
        self.screen.blit(kills, kills_rect)

        lives = self.font_medium.render(f'VIDAS: {self.score.lives}', True, (180, 30, 30))
        lives_rect = lives.get_rect(center=(HALF_WIDTH, HEIGHT // 2 + 40))
        self.screen.blit(lives, lives_rect)

        self.present()
        self.clock.tick(60)

    def draw_game_over(self):
        self.screen.blit(self.dead_image, self.img_offset)

        overlay = pg.Surface(RES, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render('GAME OVER', True, (220, 30, 30))
        title_rect = title.get_rect(center=(HALF_WIDTH, HEIGHT // 4))
        self.screen.blit(title, title_rect)

        kills = self.font_option.render(f'{self.score.kills}', True, (255, 255, 255))
        kills_rect = kills.get_rect(center=(HALF_WIDTH, HEIGHT // 4 + 60))
        self.screen.blit(kills, kills_rect)

        kills_label = self.font_hint.render('KILLS', True, (160, 160, 160))
        kills_label_rect = kills_label.get_rect(center=(HALF_WIDTH, HEIGHT // 4 + 90))
        self.screen.blit(kills_label, kills_label_rect)

        prompt = self.font_section.render('DIGITE SEU NOME:', True, (200, 200, 200))
        prompt_rect = prompt.get_rect(center=(HALF_WIDTH, HEIGHT // 2 + 20))
        self.screen.blit(prompt, prompt_rect)

        display_name = self.player_name + '_'
        name_text = self.font_option.render(display_name, True, (220, 50, 50))
        name_rect = name_text.get_rect(center=(HALF_WIDTH, HEIGHT // 2 + 65))
        self.screen.blit(name_text, name_rect)

        if len(self.player_name) > 0:
            save_hint = self.font_hint.render('[ENTER] Salvar', True, (190, 190, 190))
            save_rect = save_hint.get_rect(center=(HALF_WIDTH, HEIGHT - 80))
            self.screen.blit(save_hint, save_rect)

        skip = self.font_hint.render('[ESC] Pular', True, (120, 120, 120))
        skip_rect = skip.get_rect(center=(HALF_WIDTH, HEIGHT - 50))
        self.screen.blit(skip, skip_rect)

        self.present()
        self.clock.tick(60)

    def draw_ranking(self):
        self.screen.fill((10, 10, 10))

        title = self.font_option.render('RANKING', True, (220, 50, 50))
        title_rect = title.get_rect(center=(HALF_WIDTH, 50))
        self.screen.blit(title, title_rect)

        pg.draw.line(self.screen, (80, 20, 20), (HALF_WIDTH - 120, 80), (HALF_WIDTH + 120, 80), 2)

        ranking = ScoreManager.load_ranking()

        if not ranking:
            empty = self.font_hint.render('Nenhum registro', True, (120, 120, 120))
            empty_rect = empty.get_rect(center=(HALF_WIDTH, HEIGHT // 2))
            self.screen.blit(empty, empty_rect)
        else:
            header_pos = self.font_small.render('POS', True, (120, 120, 120))
            header_name = self.font_small.render('NOME', True, (120, 120, 120))
            header_kills = self.font_small.render('KILLS', True, (120, 120, 120))
            col_pos = HALF_WIDTH - 220
            col_name = HALF_WIDTH - 100
            col_kills = HALF_WIDTH + 160
            y = 105
            self.screen.blit(header_pos, (col_pos, y))
            self.screen.blit(header_name, (col_name, y))
            self.screen.blit(header_kills, (col_kills, y))
            y += 30

            pg.draw.line(self.screen, (50, 50, 50), (col_pos, y), (col_kills + 80, y), 1)
            y += 15

            for i, entry in enumerate(ranking[:10]):
                if i < 3:
                    color = (220, 50, 50)
                else:
                    color = (180, 180, 180)

                pos_text = self.font_section.render(f'{i + 1:>2}.', True, color)
                name_text = self.font_section.render(entry['name'], True, color)
                kills_text = self.font_section.render(str(entry['kills']), True, color)

                self.screen.blit(pos_text, (col_pos, y))
                self.screen.blit(name_text, (col_name, y))
                kills_rect = kills_text.get_rect(topright=(col_kills + 80, y))
                self.screen.blit(kills_text, kills_rect)
                y += 38

        hint = self.font_hint.render('[ESC] Voltar', True, (120, 120, 120))
        hint_rect = hint.get_rect(center=(HALF_WIDTH, HEIGHT - 35))
        self.screen.blit(hint, hint_rect)

        self.present()
        self.clock.tick(60)

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if self.state == 'menu':
                self._handle_menu_event(event)
            elif self.state == 'instructions':
                self._handle_instructions_event(event)
            elif self.state == 'ranking':
                self._handle_ranking_event(event)
            elif self.state == 'round_intro':
                self._handle_round_intro_event(event)
            elif self.state == 'dead':
                self._handle_dead_event(event)
            elif self.state == 'game_over':
                self._handle_game_over_event(event)
            elif self.state == 'victory':
                self._handle_victory_event(event)
            elif self.state == 'playing':
                self._handle_playing_event(event)

    def _handle_menu_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_w, pg.K_UP):
                self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
            elif event.key in (pg.K_s, pg.K_DOWN):
                self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
            elif event.key == pg.K_RETURN:
                if self.menu_selected == 0:
                    self.start_game()
                elif self.menu_selected == 1:
                    self.state = 'instructions'
                elif self.menu_selected == 2:
                    self.state = 'ranking'
            elif event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()

    def _handle_instructions_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.state = 'menu'

    def _handle_ranking_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.state = 'menu'

    def _handle_round_intro_event(self, event):
        if event.type == pg.KEYDOWN:
            elapsed = pg.time.get_ticks() - self.round_intro_start
            if elapsed > 1000:
                pg.mouse.set_visible(False)
                pg.event.set_grab(True)
                self.state = 'playing'

    def _handle_victory_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN and len(self.player_name) > 0:
                self.score.save_score(self.player_name)
                self.state = 'ranking'
            elif event.key == pg.K_ESCAPE:
                self.state = 'ranking'
            elif event.key == pg.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif len(self.player_name) < self.max_name_len:
                char = event.unicode
                if char.isalnum():
                    self.player_name += char.upper()

    def _handle_dead_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                self.continue_game()
            elif event.key == pg.K_ESCAPE:
                self.go_to_menu()

    def _handle_game_over_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN and len(self.player_name) > 0:
                self.score.save_score(self.player_name)
                self.state = 'ranking'
            elif event.key == pg.K_ESCAPE:
                self.state = 'ranking'
            elif event.key == pg.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif len(self.player_name) < self.max_name_len:
                char = event.unicode
                if char.isalnum():
                    self.player_name += char.upper()

    def _handle_playing_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.go_to_menu()
            return
        elif event.type == self.global_event:
            self.global_trigger = True
        self.player.single_fire_event(event)

    def run(self):
        while True:
            self.check_events()
            if self.state == 'menu':
                self.draw_menu()
            elif self.state == 'instructions':
                self.draw_instructions()
            elif self.state == 'ranking':
                self.draw_ranking()
            elif self.state == 'round_intro':
                self.draw_round_intro()
            elif self.state == 'dead':
                self.draw_dead()
            elif self.state == 'game_over':
                self.draw_game_over()
            elif self.state == 'victory':
                self.draw_victory()
            elif self.state == 'playing':
                self.update()
                self.draw()


if __name__ == '__main__':
    game = Game()
    game.run()
