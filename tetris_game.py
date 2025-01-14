import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)  # Extra space for next piece and score
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)    # I piece
BLUE = (0, 0, 255)      # J piece
ORANGE = (255, 165, 0)  # L piece
YELLOW = (255, 255, 0)  # O piece
GREEN = (0, 255, 0)     # S piece
PURPLE = (128, 0, 128)  # T piece
RED = (255, 0, 0)       # Z piece

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0],      # J
     [1, 1, 1]],
    [[0, 0, 1],      # L
     [1, 1, 1]],
    [[1, 1],         # O
     [1, 1]],
    [[0, 1, 1],      # S
     [1, 1, 0]],
    [[0, 1, 0],      # T
     [1, 1, 1]],
    [[1, 1, 0],      # Z
     [0, 1, 1]]
]

COLORS = [CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0

    def new_piece(self):
        shape = random.choice(SHAPES)
        color = COLORS[SHAPES.index(shape)]
        # Start position - center top
        x = GRID_WIDTH // 2 - len(shape[0]) // 2
        y = 0
        return {'shape': shape, 'color': color, 'x': x, 'y': y}

    def valid_move(self, piece, x, y):
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    if not (0 <= x + j < GRID_WIDTH and 
                          y + i < GRID_HEIGHT and 
                          (y + i < 0 or self.grid[y + i][x + j] == BLACK)):
                        return False
        return True

    def rotate_piece(self, piece):
        # Get the rotated shape matrix
        rotated_shape = list(zip(*piece['shape'][::-1]))
        new_piece = {
            'shape': rotated_shape,
            'color': piece['color'],
            'x': piece['x'],
            'y': piece['y']
        }
        if self.valid_move(new_piece, new_piece['x'], new_piece['y']):
            return new_piece
        return piece

    def merge_piece(self):
        for i, row in enumerate(self.current_piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece['y'] + i][self.current_piece['x'] + j] = self.current_piece['color']

    def clear_lines(self):
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(cell != BLACK for cell in self.grid[y]):
                lines_cleared += 1
                # Move all lines above down
                for y2 in range(y, 0, -1):
                    self.grid[y2] = self.grid[y2 - 1][:]
                # Clear top line
                self.grid[0] = [BLACK] * GRID_WIDTH
            else:
                y -= 1
        self.score += lines_cleared * 100

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw grid
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                pygame.draw.rect(self.screen, color,
                               (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw current piece
        if self.current_piece:
            for i, row in enumerate(self.current_piece['shape']):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, self.current_piece['color'],
                                       ((self.current_piece['x'] + j) * BLOCK_SIZE,
                                        (self.current_piece['y'] + i) * BLOCK_SIZE,
                                        BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 10, 10))

        pygame.display.flip()

    def run(self):
        fall_time = 0
        fall_speed = 500  # Time in milliseconds before piece falls
        while not self.game_over:
            fall_time += self.clock.get_rawtime()
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.valid_move(self.current_piece, self.current_piece['x'] - 1, self.current_piece['y']):
                            self.current_piece['x'] -= 1
                    elif event.key == pygame.K_RIGHT:
                        if self.valid_move(self.current_piece, self.current_piece['x'] + 1, self.current_piece['y']):
                            self.current_piece['x'] += 1
                    elif event.key == pygame.K_DOWN:
                        if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                            self.current_piece['y'] += 1
                    elif event.key == pygame.K_UP:
                        self.current_piece = self.rotate_piece(self.current_piece)
                    elif event.key == pygame.K_SPACE:
                        while self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                            self.current_piece['y'] += 1

            # Time to move piece down
            if fall_time >= fall_speed:
                if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                    self.current_piece['y'] += 1
                else:
                    self.merge_piece()
                    self.clear_lines()
                    self.current_piece = self.new_piece()
                    if not self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y']):
                        self.game_over = True
                fall_time = 0

            self.draw()

        # Game over screen
        font = pygame.font.Font(None, 48)
        game_over_text = font.render('Game Over!', True, WHITE)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)

if __name__ == '__main__':
    game = Tetris()
    game.run()
    pygame.quit()