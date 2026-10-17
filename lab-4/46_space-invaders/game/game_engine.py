
import pygame
import random
import os

from .player import Player
from .enemy import EnemyGrid
from .bullet import Bullet


# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)


class GameEngine:
    def __init__(self, width, height, difficulty="medium"):
        self.width = width
        self.height = height

        # Create player and enemy grid
        self.player = Player(
            width // 2 - 20, height - 50, 40, 20
        )
        self.enemy_grid = EnemyGrid(width)

        # Bullet lists and shooting cooldown
        self.player_bullets = []
        self.enemy_bullets = []
        self._shoot_cooldown = 0

        # Difficulty settings
        self.difficulty = difficulty

        fire_rates = {
            "easy": 0.0004,
            "medium": 0.0008,
            "hard": 0.0016,
        }

        self.enemy_fire_chance = fire_rates.get(
            difficulty, 0.0008
        )

        # Score and game state
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over = False
        self.won = False
        self._game_over_logged = False

        # Load sound effects
        sound_dir = os.path.join(
            os.path.dirname(__file__), "sounds"
        )

        self.shoot_sound = None
        self.enemy_destroyed_sound = None
        self.game_over_sound = None
        self._game_over_sound_played = False

        # Sound is optional, so the game can still run
        # if audio is unavailable.
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            self.shoot_sound = pygame.mixer.Sound(
                os.path.join(sound_dir, "shoot.wav")
            )
            self.enemy_destroyed_sound = pygame.mixer.Sound(
                os.path.join(sound_dir, "enemy_destroyed.wav")
            )
            self.game_over_sound = pygame.mixer.Sound(
                os.path.join(sound_dir, "game_over.wav")
            )

        except (pygame.error, OSError) as error:
            print("Sound effects unavailable:", error)

    def handle_event(self, event):
        # Player shoots with SPACE
        if (
            not self.game_over
            and event.type == pygame.KEYDOWN
            and event.key == pygame.K_SPACE
        ):
            if self._shoot_cooldown <= 0:
                bullet_x = self.player.center_x() - 2

                self.player_bullets.append(
                    Bullet(
                        bullet_x,
                        self.player.y,
                        direction=-1
                    )
                )

                # Play shooting sound
                if self.shoot_sound:
                    self.shoot_sound.play()

                self._shoot_cooldown = 15

    def handle_input(self):
        # Do not move after the game ends
        if self.game_over:
            return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(-self.player.speed, self.width)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(self.player.speed, self.width)

    def update(self):
        # Stop updating after the game ends
        if self.game_over:
            return

        # Reduce shooting cooldown
        if self._shoot_cooldown > 0:
            self._shoot_cooldown -= 1

        # Move enemies
        self.enemy_grid.move()

        # Enemies shoot randomly
        for enemy in self.enemy_grid.alive_enemies():
            if random.random() < self.enemy_fire_chance:
                bullet_x = enemy.x + enemy.width // 2

                self.enemy_bullets.append(
                    Bullet(
                        bullet_x,
                        enemy.y + enemy.height,
                        direction=1
                    )
                )

        # Move bullets
        for bullet in self.player_bullets:
            bullet.move()

        for bullet in self.enemy_bullets:
            bullet.move()

        # Remove bullets that leave the screen
        self.player_bullets = [
            bullet for bullet in self.player_bullets
            if not bullet.off_screen(self.height)
        ]

        self.enemy_bullets = [
            bullet for bullet in self.enemy_bullets
            if not bullet.off_screen(self.height)
        ]

        # Player bullets hit enemies
        # Iterate over a copy because bullets are removed here.
        for bullet in self.player_bullets[:]:
            for enemy in self.enemy_grid.alive_enemies():
                if bullet.rect().colliderect(enemy.rect()):
                    enemy.alive = False
                    self.player_bullets.remove(bullet)
                    self.score += 1

                    # Play enemy destruction sound
                    if self.enemy_destroyed_sound:
                        self.enemy_destroyed_sound.play()

                    break

        # Enemy bullets hit the player
        for bullet in self.enemy_bullets:
            if bullet.rect().colliderect(self.player.rect()):
                self.game_over = True
                self.won = False
                break

        # Enemies reach the bottom: player loses
        if self.enemy_grid.reached_bottom(self.player.y):
            self.game_over = True
            self.won = False

        # All enemies destroyed: player wins
        if not self.enemy_grid.alive_enemies():
            self.game_over = True
            self.won = True

        # Play the ending sound only once
        if (
            self.game_over
            and not self._game_over_sound_played
        ):
            if self.game_over_sound:
                self.game_over_sound.play()

            self._game_over_sound_played = True

    def render(self, screen):
        # Draw player
        pygame.draw.rect(
            screen, GREEN, self.player.rect()
        )

        # Draw living enemies
        for enemy in self.enemy_grid.alive_enemies():
            pygame.draw.rect(
                screen, WHITE, enemy.rect()
            )

        # Draw player bullets
        for bullet in self.player_bullets:
            pygame.draw.rect(
                screen, WHITE, bullet.rect()
            )

        # Draw enemy bullets
        for bullet in self.enemy_bullets:
            pygame.draw.rect(
                screen, RED, bullet.rect()
            )

        # Current score
        score_text = self.font.render(
            f"Score: {self.score}", True, WHITE
        )
        screen.blit(score_text, (10, 10))

        # Game-ending screen
        if self.game_over:
            # Dark translucent overlay
            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            # Winning or losing message
            if self.won:
                message = "YOU WON!"
                message_color = GREEN
            else:
                message = "GAME OVER"
                message_color = RED

            title_text = self.font.render(
                message, True, message_color
            )
            title_rect = title_text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 - 80
                )
            )
            screen.blit(title_text, title_rect)

            # Final score
            final_score_text = self.font.render(
                f"Final Score: {self.score}",
                True,
                WHITE
            )
            final_score_rect = final_score_text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 - 30
                )
            )
            screen.blit(
                final_score_text, final_score_rect
            )

            # Replay and exit instructions
            small_font = pygame.font.SysFont("Arial", 20)

            replay_text = small_font.render(
                "Press R to Replay", True, WHITE
            )
            replay_rect = replay_text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 + 20
                )
            )
            screen.blit(replay_text, replay_rect)

            exit_text = small_font.render(
                "Press ESC to Exit", True, WHITE
            )
            exit_rect = exit_text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 + 60
                )
            )
            screen.blit(exit_text, exit_rect)

            # Print the final score once
            if not self._game_over_logged:
                print(
                    "Game over! Final score:", self.score
                )
                self._game_over_logged = True
