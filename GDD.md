# Game Design Document - Project Hellbreaker

## 1. Visao geral

| Campo | Descricao |
|---|---|
| Titulo | Project Hellbreaker |
| Genero | FPS (First-Person Shooter) |
| Plataforma | PC (Windows, Linux, macOS) |
| Engine | Python 3 + Pygame |
| Perspectiva | Primeira pessoa (pseudo-3D via raycasting) |
| Publico-alvo | Jogadores casuais e fas de shooters retro |

Project Hellbreaker e um FPS pseudo-3D inspirado em classicos como DOOM e Wolfenstein 3D. O jogador enfrenta 10 rounds de dificuldade crescente, eliminando hordas de inimigos demoniacos em um cenario fechado estilo dungeon.

## 2. Gameplay

### 2.1 Objetivo

Sobreviver e eliminar todos os inimigos nos 10 rounds. A pontuacao final e baseada no total de kills acumulados ao longo da partida.

### 2.2 Loop principal

1. O jogador inicia no menu e seleciona PLAY
2. Uma tela de introducao exibe o round atual, inimigos e dificuldade
3. O jogador e colocado no mapa e deve eliminar todos os NPCs
4. Ao eliminar todos os inimigos, avanca para o proximo round
5. Apos o round 10, a tela de vitoria e exibida
6. O jogador pode salvar seu nome no ranking

### 2.3 Condicoes de derrota

- A vida do jogador chega a zero
- Cada morte consome 1 das 3 vidas disponiveis
- Se todas as vidas acabam, e Game Over

## 3. Jogador

| Atributo | Valor |
|---|---|
| Vida maxima | 100 HP |
| Recuperacao passiva | +1 HP a cada 700ms |
| Vidas por partida | 3 |
| Velocidade | 0.004 (por delta_time) |
| Arma | Shotgun |
| Dano base | 50 |

### 3.1 Controles

| Input | Acao |
|---|---|
| W / A / S / D | Movimentacao (frente, esquerda, tras, direita) |
| Mouse (horizontal) | Rotacao da camera |
| Botao esquerdo do mouse | Disparar |
| ESC | Voltar ao menu |
| ENTER | Confirmar em telas de UI |

### 3.2 Colisao

O jogador possui colisao com paredes do mapa. A movimentacao diagonal e corrigida por um fator de 1/sqrt(2) para manter velocidade constante.

## 4. Inimigos (NPCs)

### 4.1 Tipos

| Tipo | Vida | Dano | Velocidade | Precisao | Dist. ataque | Categoria |
|---|---|---|---|---|---|---|
| Soldier | 100 | 10 | 0.03 | 15% | 3-6 tiles | Normal |
| Caco Demon | 150 | 25 | 0.05 | 35% | 1 tile | Demonio |
| Cyber Demon | 350 | 15 | 0.055 | 25% | 6 tiles | Demonio |

### 4.2 Comportamento (IA)

- **Idle**: Permanece parado ate avistar o jogador
- **Perseguicao**: Ao detectar o jogador (via raycast), se move em direcao a ele usando pathfinding BFS
- **Ataque**: Quando dentro da distancia de ataque, executa animacao de ataque e causa dano baseado na precisao
- **Dor**: Ao receber dano, executa animacao de dor brevemente
- **Morte**: Ao perder toda a vida, executa animacao de morte. O kill so e contabilizado no ultimo frame da animacao

### 4.3 Pathfinding

Os NPCs utilizam BFS (Busca em Largura) com 8 direcoes para navegar pelo mapa. Posicoes ocupadas por outros NPCs sao evitadas.

### 4.4 Deteccao do jogador

Cada NPC executa um raycast proprio em direcao ao jogador para verificar linha de visao. Se nao houver parede entre o NPC e o jogador, a deteccao e positiva.

## 5. Sistema de rounds

### 5.1 Progressao

| Round | Inimigos | Composicao |
|---|---|---|
| 1 | 5 | 100% Soldados |
| 2 | 7 | 100% Soldados |
| 3 | 9 | 75% Soldados, 25% Caco Demons |
| 4 | 11 | 75% Soldados, 25% Caco Demons |
| 5 | 13 | 55% Soldados, 30% Caco Demons, 15% Cyber Demons |
| 6 | 15 | 55% Soldados, 30% Caco Demons, 15% Cyber Demons |
| 7 | 17 | 40% Soldados, 30% Caco Demons, 30% Cyber Demons |
| 8 | 19 | 40% Soldados, 30% Caco Demons, 30% Cyber Demons |
| 9 | 21 | 25% Soldados, 35% Caco Demons, 40% Cyber Demons |
| 10 | 23 | 25% Soldados, 35% Caco Demons, 40% Cyber Demons |

### 5.2 Spawn de NPCs

Os NPCs sao spawnados apenas em tiles acessiveis ao jogador (verificado via BFS a partir da posicao inicial). O sistema tenta espalhar os NPCs com distancia minima decrescente (4.0 -> 2.5 -> 1.5 tiles). Se necessario, o fallback final spawna sem restricao de distancia para garantir que o round tenha inimigos suficientes.

### 5.3 Area restrita

A regiao (0-9, 0-9) e uma area restrita onde NPCs nao sao spawnados, evitando que aparecam muito perto do ponto de inicio do jogador.

## 6. Sistema de power-ups

### 6.1 Damage Boost

- **Origem**: Dropado ao matar inimigos do tipo Demonio (Caco Demon e Cyber Demon)
- **Efeito**: Aumenta o dano da arma em +50% por stack
- **Duracao**: 5 segundos por stack
- **Stackavel**: Sim, cada boost coletado adiciona um stack independente
- **Coleta**: Automatica ao se aproximar (distancia < 0.8 tiles)
- **Indicador**: HUD na parte inferior da tela exibindo multiplicador atual, barra de tempo e segundos restantes

### 6.2 Calculo de dano

```
dano_final = dano_base * (1 + quantidade_stacks * 0.5)
```

Exemplos: 0 stacks = 50, 1 stack = 75, 2 stacks = 100.

## 7. Mapa

### 7.1 Estrutura

O mapa e definido como uma grid 16x32 onde cada celula pode ser:

| Valor | Significado |
|---|---|
| 0 (False) | Chao (area transitavel) |
| 1 | Parede tipo 1 |
| 2 | Parede tipo 2 |
| 3 | Parede tipo 3 |
| 4 | Parede tipo 4 |
| 5 | Parede tipo 5 |

### 7.2 Objetos decorativos

O mapa contem sprites animados (luzes verdes e vermelhas) posicionados em locais fixos para ambientacao.

## 8. Renderizacao

### 8.1 Raycasting

O motor de renderizacao utiliza raycasting com resolucao de 640 raios (metade da largura da tela). Para cada raio:

1. Calcula intersecoes horizontais e verticais com as paredes
2. Determina a profundidade e textura da parede mais proxima
3. Projeta a parede na tela com altura proporcional a distancia
4. Aplica correcao de fishbowl effect

### 8.2 Sprites

Sprites (NPCs, decoracoes, pickups) sao renderizados apos as paredes, ordenados por profundidade (de tras para frente). Cada sprite e projetado na tela de acordo com sua posicao relativa ao jogador.

### 8.3 HUD

- HP com digitos graficos (canto superior esquerdo)
- Round atual e kills (centro superior)
- Vidas restantes como cruzes vermelhas (canto superior direito)
- Indicador de damage boost (centro inferior, quando ativo)

### 8.4 Resolucao

| Parametro | Valor |
|---|---|
| Resolucao interna | 1280 x 720 |
| Resolucao da janela | 1280 x 720 |
| FOV | 60 graus |
| Tamanho de textura | 256 x 256 |

## 9. Audio

| Som | Descricao |
|---|---|
| theme.mp3 | Musica de fundo durante o gameplay (loop) |
| shotgun.wav | Disparo da arma |
| npc_pain.wav | NPC recebendo dano |
| npc_death.wav | NPC morrendo |
| npc_attack.wav | NPC atacando |
| player_pain.wav | Jogador recebendo dano |

## 10. Interface (UI)

### 10.1 Estados do jogo

```
menu -> round_intro -> playing -> round_intro (proximo round)
                                -> dead -> round_intro (continuar)
                                        -> menu (ESC)
                                -> game_over -> ranking
                                -> victory -> ranking
menu -> instructions -> menu
menu -> ranking -> menu
```

### 10.2 Telas

- **Menu**: Fundo com imagem, opcoes PLAY / INSTRUCOES / RANKING
- **Instrucoes**: Controles e informacoes do sistema de rounds
- **Round Intro**: Animacao com numero do round, descricao tematica, lista de inimigos, barra de progresso e estatisticas
- **Playing**: Gameplay em primeira pessoa com HUD
- **Voce Morreu**: Exibida ao perder uma vida, mostra round e kills
- **Game Over**: Sem vidas restantes, permite digitar nome para ranking
- **Vitoria**: Apos completar o round 10, exibe kills totais e campo de nome
- **Ranking**: Top 10 jogadores ordenados por kills

## 11. Persistencia

O ranking e salvo em `ranking.json` no diretorio do jogo. Armazena no maximo 10 entradas, ordenadas por numero de kills em ordem decrescente. Cada entrada contem nome (maximo 8 caracteres alfanumericos) e quantidade de kills.

## 12. Requisitos tecnicos

| Requisito | Especificacao |
|---|---|
| Linguagem | Python 3.8+ |
| Biblioteca principal | Pygame |
| Dependencias | Apenas Pygame |
| Sistema operacional | Windows, Linux, macOS |
| Hardware minimo | Qualquer PC capaz de rodar Python |
