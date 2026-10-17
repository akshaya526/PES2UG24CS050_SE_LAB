
import pygame
from game.game_engine import GameEngine

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Pygame Version")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)

# Clock
clock = pygame.time.Clock()
FPS = 60


def select_difficulty():
    title_font = pygame.font.SysFont("Arial", 42)
    font = pygame.font.SysFont("Arial", 28)
    small_font = pygame.font.SysFont("Arial", 20)

    while True:
        SCREEN.fill(BLACK)

        # Game title
        title = title_font.render(
            "SPACE INVADERS", True, GREEN
        )
        SCREEN.blit(
            title,
            title.get_rect(center=(WIDTH // 2, 230))
        )

        # Menu heading
        heading = font.render(
            "Select Difficulty", True, WHITE
        )
        SCREEN.blit(
            heading,
            heading.get_rect(center=(WIDTH // 2, 310))
        )

        # Difficulty options
        options = [
            ("1 - Easy", GREEN),
            ("2 - Medium", WHITE),
            ("3 - Hard", RED),
        ]

        for index, (label, color) in enumerate(options):
            text = font.render(label, True, color)
            SCREEN.blit(
                text,
                text.get_rect(
                    center=(WIDTH // 2, 375 + index * 45)
                )
            )

        hint = small_font.render(
            "Press 1, 2, or 3 to start",
            True,
            WHITE
        )
        SCREEN.blit(
            hint,
            hint.get_rect(center=(WIDTH // 2, 535))
        )

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "easy"
                elif event.key == pygame.K_2:
                    return "medium"
                elif event.key == pygame.K_3:
                    return "hard"


def main():
    # Select difficulty before starting
    difficulty = select_difficulty()

    if difficulty is None:
        pygame.quit()
        return

    # Create the initial game
    engine = GameEngine(WIDTH, HEIGHT, difficulty)
    running = True

    # Main game loop
    while running:
        SCREEN.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and engine.game_over:
                if event.key == pygame.K_r:
                    # Restart with the same difficulty
                    engine = GameEngine(
                        WIDTH, HEIGHT, difficulty
                    )

                elif event.key == pygame.K_ESCAPE:
                    # Exit after Game Over
                    running = False

            else:
                engine.handle_event(event)

        if running:
            engine.handle_input()
            engine.update()
            engine.render(SCREEN)

            pygame.display.flip()
            clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
