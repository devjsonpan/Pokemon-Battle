# Took Inspiration from the video below :))
# https://www.youtube.com/watch?v=Qbg2ZunNfJY

import pygame
from pygame.locals import *
import time
import math
import random
import requests
import io
from urllib.request import urlopen

pygame.init()

# create the game window
game_width = 500
game_height = 500
size = (game_width, game_height)
game = pygame.display.set_mode(size)
pygame.display.set_caption('Pokemon Battle')

# define colors
black = (0, 0, 0)
gold = (218, 165, 32)
grey = (200, 200, 200)
green = (0, 200, 0)
light_green = (173,230,187)
light_orange = (255, 204, 153)
red = (255, 187, 173)
white = (255, 255, 255)
blue = (173, 216, 230)
dark_grey = (169, 169, 169)
light_grey = (211, 211, 211)
purple = (147, 112, 219)
orange = (255, 165, 0)
yellow = (255, 255, 0)
pink = (255, 192, 203)
background_color = (245, 245, 245)
combat_background_sky_color = (135, 206, 235)
combat_background_grass_color = (34, 139, 34)

# base url of the API
base_url = 'https://pokeapi.co/api/v2'

# Status condition constants
STATUS_NONE = 0
STATUS_BURN = 1
STATUS_PARALYSIS = 2
STATUS_POISON = 3
STATUS_SLEEP = 4
STATUS_CONFUSION = 5

player_status_checked = False

# Move names for each Pokemon
MOVE_NAMES = {
    'Raichu': 'Thunder Wave',
    'Charizard': 'Blast Burn',
    'Nidoking': 'Toxic',
    'Venusaur': 'Sleep Powder',
    'Gyarados': 'Confuse Ray',
    'Dragonite': 'Dragon Dance'
}

# Weakness chart (attacker type -> defender type)
WEAKNESSES = {
    'Fire': 'Water',
    'Water': 'Electric',
    'Electric': 'Ground',
    'Ground': 'Grass',
    'Grass': 'Fire',
    'Dragon': None  
}

# Helper function to check if an attack is super effective
def is_super_effective(attacker_type, defender_type, defender_weakness):
    # Check if the defender has a specific weakness attribute
    if defender_weakness:
        return attacker_type == defender_weakness
    
    # Check the type cycle weakness
    if defender_type in WEAKNESSES:
        weak_to = WEAKNESSES[defender_type]
        if weak_to and attacker_type == weak_to:
            return True
    
    return False

# Helper function to update the battle screen display
def update_display():
    game.fill(combat_background_grass_color)
    pygame.draw.rect(game, combat_background_sky_color, (0, 0, game_width, 150))
    
    # Draw both Pokemon if they exist
    if player_pokemon and rival_pokemon:
        player_pokemon.draw(draw_grass_pad=True)
        rival_pokemon.draw(draw_grass_pad=True)
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
    
    pygame.display.update()
    
class Pokemon(pygame.sprite.Sprite):
    
    def __init__(self, name, type, x, y, hp, attack, status_ability=None, weakness=None):
        
        pygame.sprite.Sprite.__init__(self)
        
        # call the pokemon API endpoint
        req = requests.get(f'{base_url}/pokemon/{name.lower()}')
        self.json = req.json()
        
        # set the pokemon's name and type
        self.name = name
        self.type = type 
        
        # set the sprite position on the screen
        self.x = x
        self.y = y
        
        # set the pokemon's stats (TCG Pocket style - lower numbers)
        self.current_hp = hp
        self.max_hp = hp
        self.attack = attack
        
        # status conditions
        self.status = STATUS_NONE
        self.status_ability = status_ability  # which status this pokemon can inflict
        
        # weakness (specific type this Pokemon is weak to)
        self.weakness = weakness
        
        # number of potions left
        self.num_potions = 2
                
        # set the sprite's width
        self.size = 150
        
        # set the sprite to the front facing sprite
        self.set_sprite('front_default')
    
    # Check and apply status effects at the START of the turn
    def check_status_at_turn_start(self):
        # Paralysis: Can't act for 1 turn
        if self.status == STATUS_PARALYSIS:
            self.status = STATUS_NONE  # Remove paralysis after 1 turn
            return False  # Cannot act this turn
        
        # Burn: Flip coin to try to remove it
        elif self.status == STATUS_BURN:
            coin = random.choice(['Heads', 'Tails'])
            display_message(f'{self.name} is burned! Flipping coin...')
            time.sleep(3)
            display_message(f'Result: {coin}!')
            time.sleep(2)
            if coin == 'Heads':
                self.status = STATUS_NONE
                display_message(f'{self.name} recovered from burn!')
                time.sleep(2)
                # Update display to show status removed
                update_display()
                return True  # Can act this turn
            else:
                display_message(f'{self.name} is still burned!')
                time.sleep(2)
                return True  # Can still act, will take damage at end of turn
        
        # Sleep: Flip coin to wake up
        elif self.status == STATUS_SLEEP:
            coin = random.choice(['Heads', 'Tails'])
            display_message(f'{self.name} is asleep! Flipping coin...')
            time.sleep(3)
            display_message(f'Result: {coin}!')
            time.sleep(2)
            if coin == 'Heads':
                self.status = STATUS_NONE
                display_message(f'{self.name} woke up!')
                time.sleep(2)
                # Update display to show status removed
                update_display()
                return True  # Can act this turn
            else:
                display_message(f'{self.name} is still asleep!')
                time.sleep(2)
                return False  # Cannot act
        
        return True  # Can act
    
    # Perform an attack on another Pokemon
    def perform_attack(self, other):
        # Get move name
        move_name = MOVE_NAMES.get(self.name, 'Attack')
        
        # Check confusion WHEN attacking
        if self.status == STATUS_CONFUSION:
            coin = random.choice(['Heads', 'Tails'])
            display_message(f'{self.name} is confused! Flipping coin...')
            time.sleep(3)
            display_message(f'Result: {coin}!')
            time.sleep(2)
            if coin == 'Heads':
                # Wake up from confusion and attack normally
                self.status = STATUS_NONE
                display_message(f'{self.name} snapped out of confusion!')
                time.sleep(2)
                update_display()
                time.sleep(2)
            else:
                # Attack fails and confusion is removed
                self.status = STATUS_NONE
                display_message(f'{self.name} missed due to confusion!')
                time.sleep(2)
                other.apply_status_damage_at_turn_end()
                return  # Turn ends, no damage
        
        # Calculate damage
        damage = self.attack
        
        # Check for weakness (super effective)
        is_super = is_super_effective(self.type, other.type, other.weakness)
        if is_super:
            damage += 10  # Add 10 damage for super effective attacks
            super_effective_message = True
        else:
            super_effective_message = False
        
        # Missed attack (25% chance)
        missed_attack = False
        random_num = random.randint(1, 4)
        if random_num == 1:
            damage = 0
            missed_attack = True
        
        # Display move used
        display_message(f'{self.name} uses {move_name}!')
        time.sleep(2)
        
        # Apply damage
        if missed_attack:
            display_message('Attack missed!')
            time.sleep(2)
            if other.status == STATUS_BURN or other.status == STATUS_POISON:
                other.apply_status_damage_at_turn_end()
        else:
            other.take_damage(damage)
            display_message(f'{self.name} deals {damage} damage!')
            time.sleep(2)
            
            # Display super effective message if applicable
            if is_super and super_effective_message:
                display_message(f'{move_name} was super effective!')
                time.sleep(2)
            
            # Update the display to show HP change immediately
            update_display()
            time.sleep(1)
        
        # Apply status condition based on ability (immediately)
        if self.status_ability and not missed_attack:
            if self.status_ability == STATUS_BURN:
                # Burn has 50% chance 
                if random.randint(1, 2) == 1: 
                    other.status = STATUS_BURN
                    other.take_damage(20)
                    display_message(f'{other.name} is burned!')
                    time.sleep(2)
                else:
                    display_message(f'{other.name} resisted the burn!')
                    time.sleep(2)
            
            elif self.status_ability == STATUS_POISON:
                # Poison is guaranteed (100%)
                other.status = STATUS_POISON
                other.take_damage(10)
                display_message(f'{other.name} is poisoned!')
                time.sleep(2)
            
            elif self.status_ability == STATUS_PARALYSIS:
                # Paralysis has 50% chance
                if random.randint(1, 2) == 1:
                    other.status = STATUS_PARALYSIS
                    display_message(f'{other.name} is paralyzed!')
                    time.sleep(2)
                else:
                    display_message(f'{other.name} resisted the paralysis!')
                    time.sleep(2)
            
            elif self.status_ability == STATUS_SLEEP:
                # Sleep has 75% chance
                if random.randint(1, 4) <= 3: 
                    other.status = STATUS_SLEEP
                    display_message(f'{other.name} fell asleep!')
                    time.sleep(2)
                else:
                    display_message(f'{other.name} stayed awake!')
                    time.sleep(2)
            
            elif self.status_ability == STATUS_CONFUSION:
                # Confusion is guaranteed (100%)
                other.status = STATUS_CONFUSION
                display_message(f'{other.name} is confused!')
                time.sleep(2)
            
            # Update the display to show status condition immediately
            update_display()
            time.sleep(1)
    
    # Apply status damage at the END of the turn
    def apply_status_damage_at_turn_end(self):
        # Burn: Take 20 damage at end of turn (if still burned)
        if self.status == STATUS_BURN:
            self.take_damage(20)
            display_message(f'{self.name} took 20 burn damage!')
            time.sleep(2)
            # Update display to show HP change
            update_display()
            time.sleep(1)
        
        # Poison: Take 10 damage at end of turn
        elif self.status == STATUS_POISON:
            self.take_damage(10)
            display_message(f'{self.name} took 10 poison damage!')
            time.sleep(2)
            # Update display to show HP change
            update_display()
            time.sleep(1)
        
        # Paralysis: Remove it at end of turn
        elif self.status == STATUS_PARALYSIS:
            self.status = STATUS_NONE
            display_message(f'{self.name} is no longer paralyzed!')
            time.sleep(2)
            # Update display to show status removed
            update_display()
            time.sleep(1)
    
    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0
    
    def use_potion(self):
        if self.num_potions > 0:
            # Heal 50 HP
            self.current_hp += 50
            if self.current_hp > self.max_hp:
                self.current_hp = self.max_hp
            self.num_potions -= 1
            
            # Cure status conditions
            had_status = self.status != STATUS_NONE
            self.status = STATUS_NONE
            
            display_message(f'{self.name} uses a potion and heals 50 HP!')
            time.sleep(2)
            if had_status:
                display_message(f'{self.name} is cured from all status effects!')
                time.sleep(2)
                
            # Update display to show HP change and status removed
            update_display()
            time.sleep(1)
            
            return True
        return False
    
    def set_sprite(self, side):
        image = self.json['sprites'][side]
        image_stream = urlopen(image).read()
        image_file = io.BytesIO(image_stream)
        self.image = pygame.image.load(image_file).convert_alpha()
        
        scale = self.size / self.image.get_width()
        new_width = self.image.get_width() * scale 
        new_height = self.image.get_height() * scale 
        self.image = pygame.transform.scale(self.image, (int(new_width), int(new_height)))
    
    def draw(self, alpha=255, draw_grass_pad=False):    
        if draw_grass_pad:
            oval_width = self.size * 1.2
            oval_height = self.size / 6
            oval_x = self.x + (self.size - oval_width) / 2
            oval_y = self.y + self.size - oval_height * 1.35
            pygame.draw.ellipse(game, green, (oval_x, oval_y, oval_width, oval_height))
            
        sprite = self.image.copy()
        transparency = (255, 255, 255, alpha)
        sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)
        game.blit(sprite, (self.x, self.y))
        
    def draw_hp(self):
        current_hp_int = int(self.current_hp)
        
        # Display the health bar
        bar_width = 200
        bar_height = 20
        fill_width = int((current_hp_int / self.max_hp) * bar_width)
        
        # Background (red)
        pygame.draw.rect(game, red, (self.hp_x, self.hp_y, bar_width, bar_height))
        # Foreground (green)
        pygame.draw.rect(game, green, (self.hp_x, self.hp_y, fill_width, bar_height))
        # Border
        pygame.draw.rect(game, black, (self.hp_x, self.hp_y, bar_width, bar_height), 2)
        
        # Display HP text
        hp_text = f'HP: {current_hp_int} / {self.max_hp}'
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render(hp_text, True, black)
        text_rect = text.get_rect()
        text_rect.x = self.hp_x
        text_rect.y = self.hp_y + 25
        game.blit(text, text_rect)
        
        # Display status condition
        if self.status != STATUS_NONE:
            status_text = ""
            status_color = black
            if self.status == STATUS_BURN:
                status_text = "BRN"
                status_color = orange
            elif self.status == STATUS_PARALYSIS:
                status_text = "PAR"
                status_color = yellow
            elif self.status == STATUS_POISON:
                status_text = "PSN"
                status_color = purple
            elif self.status == STATUS_SLEEP:
                status_text = "SLP"
                status_color = grey
            elif self.status == STATUS_CONFUSION:
                status_text = "CNF"
                status_color = pink
            
            # Create status background rectangle
            status_bg_width = 50
            status_bg_height = 20
            status_bg_x = self.hp_x + bar_width + 10
            status_bg_y = self.hp_y
            status_bg = pygame.Rect(status_bg_x, status_bg_y, status_bg_width, status_bg_height)
            
            # Draw status background and border
            pygame.draw.rect(game, status_color, status_bg)
            pygame.draw.rect(game, black, status_bg, 2)
            
            # Create and center status text
            status_surface = font.render(status_text, True, black)
            
            # Get text rectangle and center it within the background
            status_text_rect = status_surface.get_rect(center=status_bg.center)
            game.blit(status_surface, status_text_rect)
        
    def get_rect(self):
        return Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

def display_message(message):
    pygame.draw.rect(game, white, (10, 350, 480, 140))
    pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
    
    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    text = font.render(message, True, black)
    text_rect = text.get_rect()
    text_rect.x = 30
    text_rect.y = 410
    game.blit(text, text_rect)
    
    pygame.display.update()
    
def create_button(width, height, left, top, text_cx, text_cy, label, highlight=False):
    mouse_cursor = pygame.mouse.get_pos()
    button = Rect(left, top, width, height)
    
    if highlight or button.collidepoint(mouse_cursor):
        pygame.draw.rect(game, light_grey, button)
    else:
        pygame.draw.rect(game, grey, button)
        
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render(f'{label}', True, black)
    text_rect = text.get_rect(center=(text_cx, text_cy))
    game.blit(text, text_rect)
    
    return button

def draw_main_menu():
    game.fill(background_color)
    pygame.draw.polygon(game, red, [(0, 0), (game_width, 0), (0, game_height)])
    pygame.draw.polygon(game, white, [(game_width, game_height), (game_width, 0), (0, game_height)])
    font = pygame.font.Font(pygame.font.get_default_font(), 36)
    title = font.render("Pokemon Battle", True, black)
    title_rect = title.get_rect(center=(game_width // 2, game_height // 4))
    game.blit(title, title_rect)

    instructions_button = create_button(240, 50, 130, 200, 250, 225, 'Instructions')
    play_button = create_button(240, 50, 130, 275, 250, 300, 'Play Game')

    pygame.display.update()
    return instructions_button, play_button

def draw_instructions():
    game.fill(background_color)
    pygame.draw.polygon(game, white, [(0, 0), (game_width, 0), (0, game_height)])
    pygame.draw.polygon(game, light_green, [(game_width, game_height), (game_width, 0), (0, game_height)])
    font = pygame.font.Font(pygame.font.get_default_font(), 14)
    lines = [
        "How to Play:",
        "1. On your turn, you may attack and/or use potions (2 in total)",
        "2. Each potion heals 50 HP and removes all status effects",
        "3. Status Effects:",
        "   - Burn (50% chance per attack): 20 dmg/turn, coin flip to remove",
        "   - Poison (100% chance per attack): 10 dmg/turn, permanent",
        "   - Sleep (75% chance per attack): Requires coin flip to wake up",
        "   - Paralysis (50% chance per attack): Can't attack/heal for 1 turn",
        "   - Confusion (100% chance per attack): Must flip coin to attack",
        "4. Type weaknesses result in super effective attacks (+10 damage)",
        "5. First to reduce opponent's HP to 0 wins!",
    ]
    y = 30
    for line in lines:
        text = font.render(line, True, black)
        text_rect = text.get_rect(left=10, top=y)
        game.blit(text, text_rect)
        y += 38

    pygame.draw.rect(game, white, (150, 445, 200, 40))
    pygame.draw.rect(game, black, (150, 445, 200, 40), 2)
    text = font.render("Press 'B' to go back", True, black)
    text_rect = text.get_rect(center=(game_width // 2, 465))
    game.blit(text, text_rect)

    pygame.display.update()
    
def draw_pokemon_select_screen(pokemons):
    game.fill(background_color)
    pygame.draw.polygon(game, white, [(0, 0), (game_width, 0), (0, game_height)])
    pygame.draw.polygon(game, blue, [(game_width, game_height), (game_width, 0), (0, game_height)])
    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    
    attack_label = font.render("Select your Pokemon", True, black)
    attack_rect = attack_label.get_rect(center=(game_width // 2, 50))
    game.blit(attack_label, attack_rect)

    for pokemon in pokemons:
        pokemon.size = 100
        pokemon.set_sprite('front_default')

    for i, pokemon in enumerate(pokemons):
        if i < 3:
            pokemon.x = 50 + i * (pokemon.size + 50)
            pokemon.y = 100
        elif i < 6:
            pokemon.x = 50 + (i - 3) * (pokemon.size + 50)
            pokemon.y = 250

        rect = pokemon.get_rect()

        mouse_cursor = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_cursor):
            pygame.draw.rect(game, light_grey, rect)
        else:
            pygame.draw.rect(game, grey, rect)
        
        pygame.draw.rect(game, black, rect, 2)
        pokemon.draw()

        name_text = font.render(pokemon.name, True, black)
        name_rect = name_text.get_rect(center=(pokemon.x + pokemon.image.get_width() // 2, pokemon.y + pokemon.image.get_height() + 17))
        game.blit(name_text, name_rect)
        
        button_main_menu = create_button(150, 50, 20, 425, 95, 450, 'Main Menu')
        button_stats = create_button(150, 50, 330, 425, 405, 450, 'Stats')

    pygame.display.update()
    return button_main_menu, button_stats

current_pokemon_index = 0

def draw_pokemon_stats_screen(pokemons, index):
    game.fill(background_color)
    pygame.draw.polygon(game, light_orange, [(0, 0), (game_width, 0), (0, game_height)])
    pygame.draw.polygon(game, white, [(game_width, game_height), (game_width, 0), (0, game_height)])
    font = pygame.font.Font(pygame.font.get_default_font(), 18)

    title = font.render("Pokemon Stats", True, black)
    title_rect = title.get_rect(center=(game_width // 2, 30))
    game.blit(title, title_rect)

    pokemon = pokemons[index]
    
    status_names = {
        STATUS_BURN: "Burn",
        STATUS_PARALYSIS: "Paralysis", 
        STATUS_POISON: "Poison",
        STATUS_SLEEP: "Sleep",
        STATUS_CONFUSION: "Confusion",
        None: "None"
    }
    
    move_name = MOVE_NAMES.get(pokemon.name, 'Attack')
    
    # Get weakness display text
    if pokemon.weakness:
        weakness_text = f"Weakness: {pokemon.weakness}"
    else:
        # Check the type cycle weakness
        if pokemon.type in WEAKNESSES and WEAKNESSES[pokemon.type]:
            weakness_text = f"Weakness: {WEAKNESSES[pokemon.type]}"
        else:
            weakness_text = "Weakness: None"
    
    pokemon_details = [
        f"Name: {pokemon.name}",
        f"Type: {pokemon.type}",
        weakness_text,
        f"HP: {pokemon.max_hp}",
        f"Attack: {pokemon.attack}",
        f"Move: {move_name}",
        f"Effect: {status_names.get(pokemon.status_ability, 'None')}"
    ]
    
    pokemon_image = pygame.transform.scale(pokemon.image, (330, 330))
    game.blit(pokemon_image, (game_width - 310, 70))

    y = 90
    for detail in pokemon_details:
        text = font.render(detail, True, black)
        text_rect = text.get_rect(left=30, top=y)
        game.blit(text, text_rect)
        y += 32

    button_previous = create_button(100, 50, 20, 400, 70, 425, 'Previous')
    button_next = create_button(100, 50, 380, 400, 430, 425, 'Next')

    pygame.draw.rect(game, white, (150, 400, 200, 50))
    pygame.draw.rect(game, black, (150, 400, 200, 50), 2)
    text = font.render("Press 'B' to go back", True, black)
    text_rect = text.get_rect(center=(game_width // 2, 425))
    game.blit(text, text_rect)

    pygame.display.update()
    return button_previous, button_next
    
# Create the pokemons with their specific weaknesses
raichu = Pokemon('Raichu', 'Electric', 25, 50, 140, 30, STATUS_PARALYSIS, weakness='Ground')
charizard = Pokemon('Charizard', 'Fire', 175, 50, 180, 40, STATUS_BURN, weakness='Water')
venusaur = Pokemon('Venusaur', 'Grass', 325, 50, 230, 25, STATUS_SLEEP, weakness='Fire')
gyarados = Pokemon('Gyarados', 'Water', 25, 200, 160, 45, STATUS_CONFUSION, weakness='Electric')
nidoking = Pokemon('Nidoking', 'Poison/Ground', 175, 200, 150, 35, STATUS_POISON, weakness='Grass')
dragonite = Pokemon('Dragonite', 'Dragon', 325, 200, 190, 50, None, weakness=None)  # Dragon has no weakness
pokemons = [raichu, charizard, venusaur, gyarados, nidoking, dragonite]

player_pokemon = None
rival_pokemon = None

game_status = 'main menu'
instructions_button = None
play_button = None
button_main_menu = None
button_stats = None
button_previous = None
button_next = None

while game_status != 'quit':
    
    for event in pygame.event.get():
        if event.type == QUIT:
            game_status = 'quit'
            
        if event.type == KEYDOWN:
            
            if event.key == K_y and game_status == 'gameover':
                raichu = Pokemon('Raichu', 'Electric', 25, 50, 140, 30, STATUS_PARALYSIS, weakness='Ground')
                charizard = Pokemon('Charizard', 'Fire', 175, 50, 180, 40, STATUS_BURN, weakness='Water')
                venusaur = Pokemon('Venusaur', 'Grass', 325, 50, 230, 25, STATUS_SLEEP, weakness='Fire')
                gyarados = Pokemon('Gyarados', 'Water', 25, 200, 160, 45, STATUS_CONFUSION, weakness='Electric')
                nidoking = Pokemon('Nidoking', 'Poison/Ground', 175, 200, 150, 35, STATUS_POISON, weakness='Grass')
                dragonite = Pokemon('Dragonite', 'Dragon', 325, 200, 190, 50, None, weakness=None)
                pokemons = [raichu, charizard, venusaur, gyarados, nidoking, dragonite]
                game_status = 'select pokemon'
                
            elif event.key == K_n:
                game_status = 'quit'
            
            elif event.key == K_b and game_status == 'instructions':
                game_status = 'main menu'
                
            elif event.key == K_b and game_status == 'pokemon stats':
                game_status = 'select pokemon'
            
        if event.type == MOUSEBUTTONDOWN:
            
            mouse_click = event.pos
            
            if game_status == 'main menu':
                if instructions_button.collidepoint(mouse_click):
                    game_status = 'instructions'
                elif play_button.collidepoint(mouse_click):
                    game_status = 'select pokemon'  
                    
            elif game_status == 'select pokemon':
                
                if button_main_menu and button_main_menu.collidepoint(mouse_click):
                    game_status = 'main menu'
                
                elif button_stats and button_stats.collidepoint(mouse_click):
                    game_status = 'pokemon stats'
                    
                for i in range(len(pokemons)):
                    
                    if pokemons[i].get_rect().collidepoint(mouse_click):
                        
                        player_pokemon = pokemons[i]
                        rival_pokemon = random.choice(pokemons)
                        
                        while rival_pokemon == player_pokemon:
                            rival_pokemon = random.choice(pokemons)
                        
                        player_pokemon.hp_x = 225
                        player_pokemon.hp_y = 275
                        rival_pokemon.hp_x = 100
                        rival_pokemon.hp_y = 50
                        
                        game_status = 'prebattle'
            
            elif game_status == 'player turn':
                update_display()
                if attack_button.collidepoint(mouse_click):
                    player_pokemon.perform_attack(rival_pokemon)
                    if rival_pokemon.current_hp == 0:
                        game_status = 'fainted'
                    else:
                        # Apply status damage/update
                        if rival_pokemon.status != STATUS_PARALYSIS:
                            player_pokemon.apply_status_damage_at_turn_end()
                        if player_pokemon.current_hp == 0:
                            game_status = 'fainted'
                        else:
                            game_status = 'rival turn'     
                    
                elif potion_button.collidepoint(mouse_click):
                    player_pokemon.use_potion()
                    # Don't end turn - stay on 'player turn' to allow attack or more potions
                                  
            elif game_status == 'pokemon stats':
                if button_previous and button_previous.collidepoint(mouse_click):
                    current_pokemon_index = (current_pokemon_index - 1) % len(pokemons)
                elif button_next and button_next.collidepoint(mouse_click):
                    current_pokemon_index = (current_pokemon_index + 1) % len(pokemons)
    
    if game_status == 'main menu':
        instructions_button, play_button = draw_main_menu()

    elif game_status == 'instructions':
        draw_instructions()
        
    elif game_status == 'select pokemon':
        button_main_menu, button_stats = draw_pokemon_select_screen(pokemons)
    
    elif game_status == 'pokemon stats':
        button_previous, button_next = draw_pokemon_stats_screen(pokemons, current_pokemon_index)
        
    elif game_status == 'prebattle':
        
        game.fill(white)
        player_pokemon.draw()
        pygame.display.update()
        
        player_pokemon.x = 0
        player_pokemon.y = 150
        rival_pokemon.x = 300
        rival_pokemon.y = 25
        
        player_pokemon.size = 200
        rival_pokemon.size = 200
        player_pokemon.set_sprite('back_default')
        rival_pokemon.set_sprite('front_default')
        
        game_status = 'start battle'
        
    elif game_status == 'start battle':
        
        alpha = 0
        while alpha < 255:
            game.fill(combat_background_grass_color)
            pygame.draw.rect(game, combat_background_sky_color, (0, 0, game_width, 150))
            rival_pokemon.draw(draw_grass_pad=True)
            rival_pokemon.draw(alpha)
            display_message(f'Rival sent out {rival_pokemon.name}!')
            alpha += .4
            pygame.display.update()
        rival_pokemon.draw_hp()
        pygame.display.update()
            
        time.sleep(1)
        
        alpha = 0
        while alpha < 255:
            player_pokemon.draw(draw_grass_pad=True)
            player_pokemon.draw(alpha)
            display_message(f'Go {player_pokemon.name}!')
            alpha += .4 
            pygame.display.update()
        player_pokemon.draw_hp()
        pygame.display.update()
        
        # Coin flip to see who goes first
        time.sleep(2)
        coin = random.choice(['Heads', 'Tails'])
        display_message(f'Flipping coin to see who goes first...')
        time.sleep(3)

        display_message(f'{coin}!')
        time.sleep(2)
        
        if coin == 'Heads': 
            display_message('Player goes first!')
            time.sleep(2)
            game_status = 'player turn'
        else:
            display_message('Rival goes first!')
            time.sleep(2)
            game_status = 'rival turn'
            
        pygame.display.update()
        
    elif game_status == 'player turn':
        
        # Check status at START of turn
        if not player_status_checked:
            can_act = player_pokemon.check_status_at_turn_start()
            player_status_checked = True  # Mark as checked
            
            if not can_act:
                # Cannot act, turn ends
                time.sleep(2)
                display_message(f'{player_pokemon.name} cannot attack this turn!')
                time.sleep(2)
                
                # Apply status damage/update
                rival_pokemon.apply_status_damage_at_turn_end() 
                player_pokemon.apply_status_damage_at_turn_end()
                if rival_pokemon.current_hp == 0:
                    game_status = 'fainted'
                else:
                    game_status = 'rival turn'
                    rival_status_checked = False  # Reset for rival's turn
                
                pygame.display.update()
                continue
            
        # Can act - show buttons
        game.fill(combat_background_grass_color)
        pygame.draw.rect(game, combat_background_sky_color, (0, 0, game_width, 150))
        player_pokemon.draw(draw_grass_pad=True)
        rival_pokemon.draw(draw_grass_pad=True)
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
            
        attack_button = create_button(240, 140, 10, 350, 130, 420, 'Attack')
        potion_button = create_button(240, 140, 250, 350, 370, 420, f'Potion ({player_pokemon.num_potions})')

        pygame.draw.line(game, black, (250, 350), (250, 490), 3)
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
            
        pygame.display.update()
        
    elif game_status == 'rival turn':
        # Reset for player's next turn
        player_status_checked = False
        
        # First, update the display
        update_display()
        
        # Check status at START of turn
        can_act = rival_pokemon.check_status_at_turn_start()
        
        if not can_act:
            # Cannot act, turn ends
            time.sleep(2)
            display_message(f'{rival_pokemon.name} cannot attack this turn!')
            time.sleep(2)
            
            # Apply status damage/update
            player_pokemon.apply_status_damage_at_turn_end()  
            rival_pokemon.apply_status_damage_at_turn_end()
            if player_pokemon.current_hp == 0:
                game_status = 'fainted'
            else:
                game_status = 'player turn'
            
            pygame.display.update()
            
        else:
            # Rival can act
            display_message('Rival is thinking...')
            time.sleep(2)

            # AI decision: use potion if low HP
            if (rival_pokemon.max_hp - rival_pokemon.current_hp >= 50) and rival_pokemon.num_potions > 0:
                rival_pokemon.use_potion()
                
                # Update the display to show the new HP and status cleared
                update_display()
                time.sleep(2) 
                rival_pokemon.perform_attack(player_pokemon)
            else:
                # AI attacks
                rival_pokemon.perform_attack(player_pokemon)
                            
            if player_pokemon.current_hp == 0:
                game_status = 'fainted'
            else:
                # Apply status damage/effect
                if player_pokemon.status != STATUS_PARALYSIS:
                    rival_pokemon.apply_status_damage_at_turn_end()
                if rival_pokemon.current_hp == 0:
                    game_status = 'fainted'
                else: 
                    game_status = 'player turn'
            
            pygame.display.update()
        
    elif game_status == 'fainted':
        
        alpha = 255
        while alpha > 0:
            
            game.fill(combat_background_grass_color)
            pygame.draw.rect(game, combat_background_sky_color, (0, 0, game_width, 150))
            player_pokemon.draw_hp()
            rival_pokemon.draw_hp()
            
            if rival_pokemon.current_hp == 0:
                player_pokemon.draw(draw_grass_pad=True)
                rival_pokemon.draw(alpha, draw_grass_pad=True)
                display_message(f'{rival_pokemon.name} fainted!')
            else:
                player_pokemon.draw(alpha, draw_grass_pad=True)
                rival_pokemon.draw(draw_grass_pad=True)
                display_message(f'{player_pokemon.name} fainted!')
            alpha -= .4
            
            pygame.display.update()
            
        game_status = 'gameover'
        
    if game_status == 'gameover':
        
        display_message('Play again (Y/N)?')
        
pygame.quit()