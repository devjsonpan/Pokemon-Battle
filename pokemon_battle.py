# References:
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

class Pokemon(pygame.sprite.Sprite):
    
    def __init__(self, name, type, x, y, hp, attack, status_ability=None):
        
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
        self.paralysis_turns = 0
        self.status_ability = status_ability  # which status this pokemon can inflict
        
        # number of potions left
        self.num_potions = 2
                
        # set the sprite's width
        self.size = 150
        
        # set the sprite to the front facing sprite
        self.set_sprite('front_default')
    
    def perform_attack(self, other):
        # Check if pokemon can attack based on status
        if self.status == STATUS_SLEEP:
            # Coin flip to wake up
            coin = random.choice(['Heads', 'Tails'])
            display_message(f'{self.name} is asleep! Flipping coin...')
            time.sleep(2)
            display_message(f'Result: {coin}!')
            time.sleep(2)
            if coin == 'Heads':
                self.status = STATUS_NONE
                display_message(f'{self.name} woke up!')
                time.sleep(2)
            else:
                display_message(f'{self.name} is still asleep and cannot attack!')
                time.sleep(2)
                return
        
        if self.status == STATUS_PARALYSIS:
            self.paralysis_turns -= 1
            if self.paralysis_turns <= 0:
                self.status = STATUS_NONE
                display_message(f'{self.name} is no longer paralyzed!')
                time.sleep(2)
            else:
                display_message(f'{self.name} is paralyzed and cannot attack!')
                time.sleep(2)
                return
        
        if self.status == STATUS_CONFUSION:
            # Coin flip to see if attack succeeds
            coin = random.choice(['Heads', 'Tails'])
            display_message(f'{self.name} is confused! Flipping coin...')
            time.sleep(2)
            display_message(f'Result: {coin}!')
            time.sleep(2)
            if coin == 'Tails':
                display_message(f'{self.name} hurt itself in confusion!')
                time.sleep(2)
                return
        
        # Calculate damage
        damage = self.attack
        
        # Missed attack (20% chance)
        missed_attack = False
        random_num = random.randint(1, 5)
        if random_num == 1:
            damage = 0
            missed_attack = True
        
        # Apply damage
        other.take_damage(damage)
        
        messages = []
        
        if missed_attack:
            messages.append('Attack missed!')
        else:
            messages.append('Hit!')
        
        messages.append(f'{self.name} dealt {damage} damage!')
        
        # Apply status condition (30% chance if not already afflicted)
        if self.status_ability and other.status == STATUS_NONE and not missed_attack:
            if random.randint(1, 10) <= 3:  # 30% chance
                other.status = self.status_ability
                if self.status_ability == STATUS_BURN:
                    messages.append(f'{other.name} was burned!')
                elif self.status_ability == STATUS_PARALYSIS:
                    other.paralysis_turns = 1
                    messages.append(f'{other.name} was paralyzed!')
                elif self.status_ability == STATUS_POISON:
                    messages.append(f'{other.name} was poisoned!')
                elif self.status_ability == STATUS_SLEEP:
                    messages.append(f'{other.name} fell asleep!')
                elif self.status_ability == STATUS_CONFUSION:
                    messages.append(f'{other.name} became confused!')
        
        # Display messages sequentially
        for message in messages:
            display_message(message)
            time.sleep(2)
    
    def apply_status_damage(self):
        """Apply end-of-turn status effects"""
        if self.status == STATUS_BURN:
            # Coin flip to heal from burn
            coin = random.choice(['Heads', 'Tails'])
            display_message(f'{self.name} is burned! Flipping coin...')
            time.sleep(2)
            display_message(f'Result: {coin}!')
            time.sleep(2)
            if coin == 'Heads':
                self.status = STATUS_NONE
                display_message(f'{self.name} healed from burn!')
                time.sleep(2)
            else:
                self.take_damage(20)
                display_message(f'{self.name} took 20 burn damage!')
                time.sleep(2)
        
        elif self.status == STATUS_POISON:
            self.take_damage(10)
            display_message(f'{self.name} took 10 poison damage!')
            time.sleep(2)
    
    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0
    
    def use_potion(self):
        if self.num_potions > 0:
            # Heal 50 HP and cure status
            self.current_hp += 50
            if self.current_hp > self.max_hp:
                self.current_hp = self.max_hp
            self.num_potions -= 1
            
            # Cure status conditions
            if self.status != STATUS_NONE:
                self.status = STATUS_NONE
                self.paralysis_turns = 0
    
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
            
            status_surface = font.render(status_text, True, white)
            status_bg = pygame.Rect(self.hp_x + bar_width + 10, self.hp_y, 50, 20)
            pygame.draw.rect(game, status_color, status_bg)
            pygame.draw.rect(game, black, status_bg, 2)
            game.blit(status_surface, (self.hp_x + bar_width + 15, self.hp_y + 2))
        
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
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    lines = [
        "How to Play:",
        "1. Select a Pokemon from the selection screen",
        "2. Battle against a rival's Pokemon",
        "3. Attack or use potions (heals 50 HP & cures status)",
        "4. Status conditions affect gameplay:",
        "   - Burn: 20 damage/turn, coin flip to heal",
        "   - Poison: 10 damage/turn",
        "   - Sleep: Can't attack, coin flip to wake",
        "   - Paralysis: Can't attack for 1 turn",
        "   - Confusion: Coin flip to attack successfully",
        "5. First to reduce opponent's HP to 0 wins!",
    ]
    y = 30
    for line in lines:
        text = font.render(line, True, black)
        text_rect = text.get_rect(center=(game_width // 2, y))
        game.blit(text, text_rect)
        y += 40

    pygame.draw.rect(game, white, (150, 440, 200, 40))
    pygame.draw.rect(game, black, (150, 440, 200, 40), 2)
    text = font.render("Press 'B' to go back", True, black)
    text_rect = text.get_rect(center=(game_width // 2, 460))
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
        else:
            pokemon.x = 150 + (i - 6) * (pokemon.size + 200)
            pokemon.y = 400

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
    
    pokemon_details = [
        f"Name: {pokemon.name}",
        f"Type: {pokemon.type}",
        f"HP: {pokemon.current_hp}/{pokemon.max_hp}",
        f"Attack: {pokemon.attack}",
        f"Status Ability: {status_names.get(pokemon.status_ability, 'None')}"
    ]
    
    pokemon_image = pygame.transform.scale(pokemon.image, (250, 250))
    game.blit(pokemon_image, (game_width - 270, 120))

    y = 90
    for detail in pokemon_details:
        text = font.render(detail, True, black)
        text_rect = text.get_rect(left=30, top=y)
        game.blit(text, text_rect)
        y += 35

    button_previous = create_button(100, 50, 20, 400, 70, 425, 'Previous')
    button_next = create_button(100, 50, 380, 400, 430, 425, 'Next')

    pygame.draw.rect(game, white, (150, 400, 200, 50))
    pygame.draw.rect(game, black, (150, 400, 200, 50), 2)
    text = font.render("Press 'B' to go back", True, black)
    text_rect = text.get_rect(center=(game_width // 2, 425))
    game.blit(text, text_rect)

    pygame.display.update()
    return button_previous, button_next
    
# Create the starter pokemons (TCG Pocket style stats: HP ~120-180, Attack ~30-70)
raichu = Pokemon('Raichu', 'Electric', 25, 50, 120, 50, STATUS_PARALYSIS)
charizard = Pokemon('Charizard', 'Fire', 175, 50, 180, 70, STATUS_BURN)
venusaur = Pokemon('Venusaur', 'Grass', 325, 50, 160, 60, STATUS_SLEEP)
gyarados = Pokemon('Gyarados', 'Water', 25, 200, 150, 65, STATUS_CONFUSION)
nidoking = Pokemon('Nidoking', 'Poison/Ground', 175, 200, 140, 55, STATUS_POISON)
dragonite = Pokemon('Dragonite', 'Dragon', 325, 200, 170, 60, None)
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
                raichu = Pokemon('Raichu', 'Electric', 25, 50, 120, 50, STATUS_PARALYSIS)
                charizard = Pokemon('Charizard', 'Fire', 175, 50, 180, 70, STATUS_BURN)
                venusaur = Pokemon('Venusaur', 'Grass', 325, 50, 160, 60, STATUS_SLEEP)
                gyarados = Pokemon('Gyarados', 'Water', 25, 200, 150, 65, STATUS_CONFUSION)
                nidoking = Pokemon('Nidoking', 'Poison/Ground', 175, 200, 140, 55, STATUS_POISON)
                dragonite = Pokemon('Dragonite', 'Dragon', 325, 200, 170, 60, None)
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
                
                if attack_button.collidepoint(mouse_click):
                    player_pokemon.perform_attack(rival_pokemon)
                    if rival_pokemon.current_hp == 0:
                        game_status = 'fainted'
                    else:
                        # Apply status damage to rival
                        rival_pokemon.apply_status_damage()
                        if rival_pokemon.current_hp == 0:
                            game_status = 'fainted'
                        else:
                            game_status = 'rival turn'
                    
                elif potion_button.collidepoint(mouse_click):
                    if player_pokemon.num_potions == 0:
                        display_message('No more potions left!')
                        time.sleep(2)
                        game_status = 'player turn'
                    else:
                        player_pokemon.use_potion()
                        display_message(f'{player_pokemon.name} used a potion!')
                        time.sleep(2)
                        game_status = 'player turn'   
                
                elif end_turn_button.collidepoint(mouse_click):
                    display_message(f'{player_pokemon.name} ended their turn!')
                    time.sleep(2)
                    rival_pokemon.apply_status_damage()
                    if rival_pokemon.current_hp == 0:
                        game_status = 'fainted'
                    else:
                        game_status = 'rival turn'
                                  
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
            
        time.sleep(1)
        
        alpha = 0
        while alpha < 255:
            player_pokemon.draw(draw_grass_pad=True)
            player_pokemon.draw(alpha)
            display_message(f'Go {player_pokemon.name}!')
            alpha += .4 
            pygame.display.update()
        
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        coin = random.choice(['Heads', 'Tails'])
        if coin == 'Heads': 
            game_status = 'rival turn'
        else:
            game_status = 'player turn'
            
        pygame.display.update()
        time.sleep(1)
        
    elif game_status == 'player turn':
        
        game.fill(combat_background_grass_color)
        pygame.draw.rect(game, combat_background_sky_color, (0, 0, game_width, 150))
        player_pokemon.draw(draw_grass_pad=True)
        rival_pokemon.draw(draw_grass_pad=True)
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        attack_button = create_button(160, 140, 10, 350, 90, 420, 'Attack')
        potion_button = create_button(160, 140, 170, 350, 250, 420, f'Potion ({player_pokemon.num_potions})')
        end_turn_button = create_button(160, 140, 330, 350, 410, 420, 'End Turn')

        pygame.draw.line(game, black, (167, 350), (167, 487), 3)
        pygame.draw.line(game, black, (333, 350), (333, 487), 3)
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
        
        pygame.display.update()
        
    elif game_status == 'rival turn':
        
        game.fill(combat_background_grass_color)
        pygame.draw.rect(game, combat_background_sky_color, (0, 0, game_width, 150))
        player_pokemon.draw(draw_grass_pad=True)
        rival_pokemon.draw(draw_grass_pad=True)
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        display_message('')
        time.sleep(2)

        if rival_pokemon.current_hp < 60 and rival_pokemon.num_potions > 0:
            rival_pokemon.use_potion()
            display_message(f'{rival_pokemon.name} used a potion!')
            pygame.display.update()  
            time.sleep(2) 
        else:
            rival_pokemon.perform_attack(player_pokemon)
        
        if player_pokemon.current_hp == 0:
            game_status = 'fainted'
        else:
            # Apply status damage to player
            player_pokemon.apply_status_damage()
            if player_pokemon.current_hp == 0:
                game_status = 'fainted'
            else:
                game_status = 'player turn'
            
        pygame.display.update()
        
    # one of the pokemons fainted
    elif game_status == 'fainted':
        
        alpha = 255
        while alpha > 0:
            
            game.fill(combat_background_grass_color)
            pygame.draw.rect(game, combat_background_sky_color, (0, 0, game_width, 150))
            player_pokemon.draw_hp()
            rival_pokemon.draw_hp()
            
            # determine which pokemon fainted
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
        
    # gameover screen
    if game_status == 'gameover':
        
        display_message('Play again (Y/N)?')
        
pygame.quit()