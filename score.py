import json
import os

RANKING_FILE = 'ranking.json'
MAX_RANKING = 10
INITIAL_LIVES = 3
MAX_ROUNDS = 10


class ScoreManager:
    def __init__(self):
        self.kills = 0
        self.lives = INITIAL_LIVES
        self.current_round = 1

    def reset(self):
        self.kills = 0
        self.lives = INITIAL_LIVES
        self.current_round = 1

    def add_kill(self):
        self.kills += 1

    def next_round(self):
        self.current_round += 1

    def is_final_round(self):
        return self.current_round >= MAX_ROUNDS

    def lose_life(self):
        self.lives -= 1
        return self.lives > 0

    def get_round_config(self):
        r = self.current_round
        enemies = 3 + r * 2
        if r <= 2:
            weights = [100, 0, 0]
        elif r <= 4:
            weights = [75, 25, 0]
        elif r <= 6:
            weights = [55, 30, 15]
        elif r <= 8:
            weights = [40, 30, 30]
        else:
            weights = [25, 35, 40]
        return enemies, weights

    def get_round_enemy_names(self):
        r = self.current_round
        if r <= 2:
            return ['Soldados']
        elif r <= 4:
            return ['Soldados', 'Caco Demons']
        elif r <= 6:
            return ['Soldados', 'Caco Demons', 'Cyber Demons']
        else:
            return ['Soldados', 'Caco Demons', 'Cyber Demons']

    def get_round_description(self):
        r = self.current_round
        descs = {
            1: 'Aquecimento',
            2: 'Esquadroes inimigos',
            3: 'Os demonios chegaram',
            4: 'Resistencia pesada',
            5: 'Inferno na terra',
            6: 'Sem misericordia',
            7: 'Horda demoniacal',
            8: 'Carnificina total',
            9: 'Apocalipse',
            10: 'Round final',
        }
        return descs.get(r, '')

    def save_score(self, name):
        ranking = self.load_ranking()
        ranking.append({'name': name.upper(), 'kills': self.kills})
        ranking.sort(key=lambda x: x['kills'], reverse=True)
        ranking = ranking[:MAX_RANKING]
        with open(RANKING_FILE, 'w') as f:
            json.dump(ranking, f, indent=2)

    @staticmethod
    def load_ranking():
        if not os.path.exists(RANKING_FILE):
            return []
        try:
            with open(RANKING_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
