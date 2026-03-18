import pygame
import random

# ==========================================
# CONSTANTS 
# ==========================================
TILE_SIZE = 30
FPS = 60 

# Movement Delays (Decoupled for balance)
PACMAN_MOVE_DELAY = 150 # ms per tile
GHOST_MOVE_DELAY = 350  # Slower ghosts! Increase this to make them even slower.

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GHOST_COLORS = [(255, 0, 0), (255, 184, 255), (0, 255, 255), (255, 184, 82)]

# Expanded Map: '#' = Wall, '.' = Pellet
LEVEL = [
    "#####################",
    "#.........#.........#",
    "#.###.###.#.###.###.#",
    "#...................#",
    "#.###.#.#####.#.###.#",
    "#.....#...#...#.....#",
    "#######.#.#.#.#######",
    "#.........#.........#",
    "#######.#.#.#.#######",
    "#.........#.........#",
    "#.###.###.#.###.###.#",
    "#...#...........#...#",
    "###.#.#.#####.#.#.###",
    "#.....#...#...#.....#",
    "#####################"
]

WIDTH = len(LEVEL[0]) * TILE_SIZE
HEIGHT = len(LEVEL) * TILE_SIZE

# ==========================================
# CLASSES
# ==========================================
class PacMan:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.score = 0
        self.dx = 0
        self.dy = 0
        self.last_move_time = pygame.time.get_ticks()

    def set_direction(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def move(self, walls, current_time):
        if current_time - self.last_move_time >= PACMAN_MOVE_DELAY:
            next_x = self.x + self.dx
            next_y = self.y + self.dy
            if (next_x, next_y) not in walls:
                self.x = next_x
                self.y = next_y
            self.last_move_time = current_time

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, 
                           (self.x * TILE_SIZE + TILE_SIZE//2, self.y * TILE_SIZE + TILE_SIZE//2), 
                           TILE_SIZE//2 - 4)

class Ghost:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.dx = 1
        self.dy = 0
        self.last_move_time = pygame.time.get_ticks()

    def move(self, walls, current_time):
        if current_time - self.last_move_time >= GHOST_MOVE_DELAY:
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            valid_moves = []

            for dx, dy in directions:
                if (self.x + dx, self.y + dy) not in walls:
                    valid_moves.append((dx, dy))

            backward_move = (-self.dx, -self.dy)
            if len(valid_moves) > 1 and backward_move in valid_moves:
                valid_moves.remove(backward_move)

            if valid_moves:
                self.dx, self.dy = random.choice(valid_moves)
                self.x += self.dx
                self.y += self.dy
            
            self.last_move_time = current_time

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, 
                         (self.x * TILE_SIZE + 4, self.y * TILE_SIZE + 4, TILE_SIZE - 8, TILE_SIZE - 8))

# ==========================================
# MAIN GAME LOOP
# ==========================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Man MVP")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    # Outer loop to handle Game Restarts
    while True:
        walls = set()
        pellets = set()
        for row_idx, row in enumerate(LEVEL):
            for col_idx, char in enumerate(row):
                if char == '#':
                    walls.add((col_idx, row_idx))
                elif char == '.':
                    pellets.add((col_idx, row_idx))

        pacman = PacMan(10, 11) 
        ghosts = [
            Ghost(9, 7, GHOST_COLORS[0]),
            Ghost(10, 7, GHOST_COLORS[1]),
            Ghost(11, 7, GHOST_COLORS[2]),
            Ghost(10, 6, GHOST_COLORS[3])
        ]

        running = True
        game_over = False
        win = False

        while running:
            current_time = pygame.time.get_ticks()

            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return  # Clean exit, avoids SystemExit error
                elif event.type == pygame.KEYDOWN:
                    if game_over:
                        if event.key == pygame.K_r:
                            running = False # Break inner loop to restart outer loop
                    else:
                        if event.key == pygame.K_UP:
                            pacman.set_direction(0, -1)
                        elif event.key == pygame.K_DOWN:
                            pacman.set_direction(0, 1)
                        elif event.key == pygame.K_LEFT:
                            pacman.set_direction(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            pacman.set_direction(1, 0)

            if not game_over:
                # 2. Update Logic
                pacman.move(walls, current_time)

                if (pacman.x, pacman.y) in pellets:
                    pellets.remove((pacman.x, pacman.y))
                    pacman.score += 1

                for ghost in ghosts:
                    ghost.move(walls, current_time)

                # Check Collisions
                for ghost in ghosts:
                    if pacman.x == ghost.x and pacman.y == ghost.y:
                        game_over = True
                
                if len(pellets) == 0:
                    game_over = True
                    win = True

            # 3. Drawing
            screen.fill(BLACK)
            
            for wall in walls:
                pygame.draw.rect(screen, BLUE, (wall[0]*TILE_SIZE, wall[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
                
            for pellet in pellets:
                pygame.draw.circle(screen, WHITE, (pellet[0]*TILE_SIZE + TILE_SIZE//2, pellet[1]*TILE_SIZE + TILE_SIZE//2), 4)

            if not game_over:
                pacman.draw(screen)
            
            for ghost in ghosts:
                ghost.draw(screen)

            # Draw UI
            score_text = font.render(f"Score: {pacman.score}", True, WHITE)
            screen.blit(score_text, (10, 10))

            if game_over:
                msg = "YOU WIN!" if win else "GAME OVER!"
                color = GREEN if win else RED
                text = font.render(f"{msg} Press 'R' to Restart", True, color)
                text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
                screen.blit(text, text_rect)

            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()