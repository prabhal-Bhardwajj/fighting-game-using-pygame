'''
This is a simple fighting game like Engine created using the Pygame library. 
It simulates a one-on-one battle between two players, each controlled by different keyboard inputs.

'''

import pygame
import sys
import os

'''
Initialize Pygame and set up constants for the game window size, frames per second (FPS), and colors.
'''
pygame.init()

'''
Set up constants for the game window size, frames per second (FPS), and colors.
'''
WIDTH, HEIGHT = 1000, 600
FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

'''
Create the game window with the specified width and height.
'''
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyFighter")

'''
Create a default background if the background image is not available.
The background consists of a light blue sky and a green ground.
'''
def create_default_background():
    bg_surface = pygame.Surface((WIDTH, HEIGHT))
    bg_surface.fill((100, 100, 255))  
    pygame.draw.rect(bg_surface, (76, 153, 0), (0, HEIGHT - 70, WIDTH, 70))  
    return bg_surface

'''
Load the background image with error handling. If the image is not found, use the default background.
'''
try:
    bg_image = pygame.image.load(os.path.join("background.jpg")).convert_alpha()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
except (pygame.error, FileNotFoundError):
    print("Background image not found, using default background")
    bg_image = create_default_background()

'''
The Fighter class represents a player in the game. Each fighter has attributes like position, health, controls, and color.
It also handles movement, attacks, and drawing the fighter on the screen.
'''
class Fighter:
    def __init__(self, x, y, flip, controls, color):
        '''
        Initialize the fighter's attributes, including size, position, velocity, health, and controls.
        '''
        self.size = (120, 200)
        self.rect = pygame.Rect(x, y, *self.size)
        self.vel_y = 0
        self.jump = False
        self.attack_type = 0
        self.health = 100
        self.flip = flip
        self.controls = controls
        self.action = "idle"
        self.color = color
        self.attacking = False
        self.attack_cooldown = 0
        
    def move(self, screen_width, screen_height, target):
        '''
        Handle the fighter's movement, jumping, and attacking. Ensure the fighter stays within the screen boundaries.
        '''
        SPEED = 8
        GRAVITY = 1.5
        JUMP_FORCE = -25
        
        dx = 0
        dy = 0
        key = pygame.key.get_pressed()
        if not self.attacking:  
            if key[self.controls[0]]:
                dx = -SPEED
                self.action = "run"
            elif key[self.controls[1]]:
                dx = SPEED
                self.action = "run"
            else:
                self.action = "idle"
            if key[self.controls[2]] and not self.jump:
                self.vel_y = JUMP_FORCE
                self.jump = True
                self.action = "jump"
            if key[self.controls[3]] and self.attack_cooldown == 0:
                self.attack(screen, target)
                self.attack_cooldown = 20
            elif key[self.controls[4]] and self.attack_cooldown == 0:
                self.attack(screen, target, True)
                self.attack_cooldown = 30
        self.vel_y += GRAVITY
        dy += self.vel_y
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 70:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 70 - self.rect.bottom
            
        self.rect.x += dx
        self.rect.y += dy
        if self.rect.colliderect(target.rect):
            if dx > 0:
                self.rect.right = target.rect.left
            elif dx < 0:
                self.rect.left = target.rect.right
    
    def attack(self, surface, target, is_kick=False):
        '''
        Perform an attack and check for collisions with the opponent. Reduce the opponent's health if hit.
        '''
        self.attacking = True
        attack_rect = pygame.Rect(
            self.rect.centerx - (2 * self.rect.width * self.flip), 
            self.rect.y,
            2 * self.rect.width,
            self.rect.height
        )
        
        if attack_rect.colliderect(target.rect):
            damage = 15 if is_kick else 10
            target.health = max(0, target.health - damage)
            
        pygame.draw.rect(surface, YELLOW, attack_rect, 2)  
        self.action = "attack"
        self.attacking = False
    
    def draw(self, surface):
        '''
        Draw the fighter, health bar, and health percentage on the screen.
        '''
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 30, self.rect.width, 20))
        health_width = self.rect.width * (self.health/100)
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 30, health_width, 20))
        pygame.draw.rect(surface, BLACK, (self.rect.x, self.rect.y - 30, self.rect.width, 20), 2)
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"{self.health}%", True, WHITE)
        surface.blit(health_text, (self.rect.centerx - 20, self.rect.y - 27))

'''
Draw the game over screen, showing the winner and instructions to restart or quit.
'''
def draw_game_over(surface, winner):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill(BLACK)
    overlay.set_alpha(128)
    surface.blit(overlay, (0, 0))
    
    font = pygame.font.Font(None, 74)
    text = font.render(f"{winner} WINS!", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    surface.blit(text, text_rect)
    
    font_small = pygame.font.Font(None, 36)
    text_restart = font_small.render("Press SPACE to restart or ESC to quit", True, WHITE)
    restart_rect = text_restart.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    surface.blit(text_restart, restart_rect)

'''
Create two fighters with different positions, controls, and colors.
Player 1 uses WASD and J/K keys, while Player 2 uses arrow keys and numpad keys.
'''
player1 = Fighter(200, 310, False, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_j, pygame.K_k), BLUE)
player2 = Fighter(700, 310, True, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_KP1, pygame.K_KP2), RED)

'''
Reset the game state by restoring the fighters' health and positions.
'''
def reset_game():
    player1.health = 100
    player1.rect.x = 200
    player1.rect.y = 310
    player2.health = 100
    player2.rect.x = 700
    player2.rect.y = 310

'''
Set up the game clock and initialize variables for the game loop.
'''
clock = pygame.time.Clock()
game_over = False
run = True

'''
Main game loop that handles events, updates the game state, and draws everything to the screen.
'''
while run:
    clock.tick(FPS)
    
    screen.blit(bg_image, (0, 0))
    
    if not game_over:
        player1.move(WIDTH, HEIGHT, player2)
        player2.move(WIDTH, HEIGHT, player1)
        player1.draw(screen)
        player2.draw(screen)
        
        if player1.health <= 0 or player2.health <= 0:
            game_over = True
            winner = "Player 2" if player1.health <= 0 else "Player 1"
    else:
        draw_game_over(screen, winner)
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            game_over = False
            reset_game()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
    
    pygame.display.update()

pygame.quit()
sys.exit()
