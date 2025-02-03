'''
Minor Changes upon the previous one
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
            elif key[self.controls[1]]:
                dx = SPEED
            if key[self.controls[2]] and not self.jump:
                self.vel_y = JUMP_FORCE
                self.jump = True
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
        self.attacking = False
    
    def draw(self, surface):
        '''
        Draw the stick figure representation of the fighter, including head, body, arms, and legs.
        Also draw the health bar and health percentage above the fighter.
        '''
        head_center = (self.rect.centerx, self.rect.top + 20)
        pygame.draw.circle(surface, self.color, head_center, 20)
        
        body_end = (head_center[0], head_center[1] + 80)
        pygame.draw.line(surface, self.color, head_center, body_end, 4)
        
        arm_start = (head_center[0], head_center[1] + 40)
        arm_length = 40
        if self.flip:
            left_arm_end = (arm_start[0] + arm_length, arm_start[1])
            right_arm_end = (arm_start[0] - arm_length, arm_start[1])
        else:
            left_arm_end = (arm_start[0] - arm_length, arm_start[1])
            right_arm_end = (arm_start[0] + arm_length, arm_start[1])
        pygame.draw.line(surface, self.color, arm_start, left_arm_end, 4)
        pygame.draw.line(surface, self.color, arm_start, right_arm_end, 4)
        
        pelvis = body_end
        leg_length = 60
        if self.flip:
            left_leg_end = (pelvis[0] + 30, pelvis[1] + leg_length)
            right_leg_end = (pelvis[0] - 30, pelvis[1] + leg_length)
        else:
            left_leg_end = (pelvis[0] - 30, pelvis[1] + leg_length)
            right_leg_end = (pelvis[0] + 30, pelvis[1] + leg_length)
        pygame.draw.line(surface, self.color, pelvis, left_leg_end, 4)
        pygame.draw.line(surface, self.color, pelvis, right_leg_end, 4)
        
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 30, self.rect.width, 20))
        health_width = self.rect.width * (self.health/100)
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 30, health_width, 20))
        pygame.draw.rect(surface, BLACK, (self.rect.x, self.rect.y - 30, self.rect.width, 20), 2)
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"{self.health}%", True, WHITE)
        surface.blit(health_text, (self.rect.centerx - 20, self.rect.y - 27))

'''
Draw the control instructions for both players on the screen.
Player 1 uses WASD and J/K keys, while Player 2 uses arrow keys and numpad keys.
'''
def draw_controls(surface):
    font = pygame.font.Font(None, 24)
    p1_text = [
        "Player 1 Controls:",
        "A/D - Move",
        "W - Jump",
        "J - Punch",
        "K - Kick"
    ]
    y = 10
    for line in p1_text:
        text = font.render(line, True, BLUE)
        surface.blit(text, (10, y))
        y += 20
    
    p2_text = [
        "Player 2 Controls:",
        "←/→ - Move",
        "↑ - Jump",
        "1 - Punch",
        "2 - Kick"
    ]
    y = 10
    for line in p2_text:
        text = font.render(line, True, RED)
        surface.blit(text, (WIDTH - 150, y))
        y += 20

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
    surface.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 30))
    
    font_small = pygame.font.Font(None, 36)
    text_restart = font_small.render("Press SPACE to restart or ESC to quit", True, WHITE)
    surface.blit(text_restart, (WIDTH//2 - text_restart.get_width()//2, HEIGHT//2 + 30))

'''
Create two fighters with different positions, controls, and colors.
Player 1 uses WASD and J/K keys, while Player 2 uses arrow keys and numpad keys.
'''
player1 = Fighter(200, 310,
