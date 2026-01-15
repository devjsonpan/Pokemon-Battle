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
background_color = (245, 245, 245)  # light grey background
combat_background_sky_color = (135, 206, 235)  # sky blue for combat
combat_background_grass_color = (34, 139, 34)  # dark green for grass

# base url of the API
base_url = 'https://pokeapi.co/api/v2'

class Pokemon(pygame.sprite.Sprite):
    
    def __init__(self, name, type, x, y, hp, attack, defense, vampirism, poison):
        
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
        
        # set the pokemon's stats
        self.current_hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self.vampirism = vampirism
        self.poison = poison
        
        # number of potions left
        self.num_potions = 3
                
        # set the sprite's width
        self.size = 150
        
        # set the sprite to the front facing sprite
        self.set_sprite('front_default')
    
    def perform_attack(self, other):
        # calculate the damage
        damage = self.attack
        
        poison = self.poison
        
        # critical hit (30% chance)
        critical_hit = False
        random_num = random.randint(1, 10)
        if random_num <= 3:
            damage *= 2
            critical_hit = True
            
             # if the attacking Pokémon is Gengar and it has the poison attribute
            if self.poison:
                # double the poison effect
                poison = self.poison * 2
        
        # missed attack (10% chance)
        missed_attack = False
        random_num = random.randint(1, 10)
        if random_num == 1:
            damage = 0
            missed_attack = True
            
        # round down the damage
        if damage > 0:
            damage = damage - other.defense
        damage = math.floor(damage)
        
        other.take_damage(damage)
        
        messages = []  # list to store messages
        
        if missed_attack:
            messages.append('Missed Attack!')
        elif critical_hit:
            messages.append('Critical Hit!')
        else:
            messages.append('Regular Hit!')
        
        messages.append(f'{self.name} dealt {damage} damage!')
        
        # apply vampirism effect if the attacking Pokémon has vampirism attribute
        if self.vampirism:
            # calculate the amount of HP restored based on the attack damage
            restored_hp = 0.5 * damage
            original_hp = self.current_hp
            # increase the current HP of the attacking Pokémon, but ensure it doesn't exceed the max HP
            self.current_hp = min(self.max_hp, self.current_hp + restored_hp)
            # append the healing message only if restored_hp is greater than 0
            if self.current_hp - original_hp > 0:
                messages.append(f'{self.name} restored {int(restored_hp)} health!')
        
        # apply poison effect if the attacking Pokémon has the poison attribute
        if self.poison and missed_attack == False:
            # reduce the opponent's current HP
            other.take_damage(poison)
            messages.append(f'{other.name} got poisoned and lost {poison} extra health!')
            
        # display messages sequentially
        for message in messages:
            display_message(message)
            time.sleep(2)
        
    def take_damage(self, damage):
        
        self.current_hp -= damage
        
        # hp should not go below 0
        if self.current_hp < 0:
            self.current_hp = 0
    
    def use_potion(self):
        
        # check if there are potions left
        if self.num_potions > 0:
            
            # add 10 hp (but don't go over the max hp)
            self.current_hp += 10
            if self.current_hp > self.max_hp:
                self.current_hp = self.max_hp
                
            # decrease the number of potions left
            self.num_potions -= 1
    
    def set_sprite(self, side):
        
        # set the pokemon's sprite
        image = self.json['sprites'][side]
        image_stream = urlopen(image).read()
        image_file = io.BytesIO(image_stream)
        self.image = pygame.image.load(image_file).convert_alpha()
        
        # scale the image
        scale = self.size / self.image.get_width()
        new_width = self.image.get_width() * scale 
        new_height = self.image.get_height() * scale 
        self.image = pygame.transform.scale(self.image, (int(new_width), int(new_height)))
    
    def draw(self, alpha=255, draw_grass_pad=False):    
        if draw_grass_pad:
            # draw green oval to represent grass pad
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
        # convert current_hp to an integer
        current_hp_int = int(self.current_hp)
        
        # display the health bar
        bar_scale = 200 // self.max_hp
        for i in range(self.max_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(game, red, bar)
            
        for i in range(current_hp_int):  
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(game, green, bar)
            
        # display whole numbers for HP
        hp_text = f'HP: {int(self.current_hp)} / {self.max_hp}'  # convert current_hp to int
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render(hp_text, True, black)
        text_rect = text.get_rect()
        text_rect.x = self.hp_x
        text_rect.y = self.hp_y + 30
        game.blit(text, text_rect)
        
    def get_rect(self):
        return Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

def display_message(message):
    
    # draw a white box with black border
    pygame.draw.rect(game, white, (10, 350, 480, 140))
    pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
    
    # display the message
    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    text = font.render(message, True, black)
    text_rect = text.get_rect()
    text_rect.x = 30
    text_rect.y = 410
    game.blit(text, text_rect)
    
    pygame.display.update()
    
def create_button(width, height, left, top, text_cx, text_cy, label, highlight=False):
    
    # position of the mouse cursor
    mouse_cursor = pygame.mouse.get_pos()
    
    button = Rect(left, top, width, height)
    
    # highlight the button if mouse is pointing to it
    if highlight or button.collidepoint(mouse_cursor):
        pygame.draw.rect(game, light_grey, button)
    else:
        pygame.draw.rect(game, grey, button)
        
    # add the label to the button
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
    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    lines = [
        "How to Play:",
        "1. Select a Pokemon from the selection screen",
        "2. Battle against a rival's Pokemon",
        "3. On your turn, you can attack or use a potion",
        "4. First to reduce the opponent's HP to 0 wins!",
        "",
    ]
    y = 50
    for line in lines:
        if line.startswith("How to Play:") or line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4."):
            text = font.render(line, True, black)
        else:
            text = font.render(line, True, black)
        text_rect = text.get_rect(center=(game_width // 2, y))
        game.blit(text, text_rect)
        y += 60

    # draw back button
    pygame.draw.rect(game, white, (150, 400, 200, 50))
    pygame.draw.rect(game, black, (150, 400, 200, 50), 2)
    text = font.render("Press 'B' to go back", True, black)
    text_rect = text.get_rect(center=(game_width // 2, 425))
    game.blit(text, text_rect)

    pygame.display.update()
    
def draw_pokemon_select_screen(pokemons):
    game.fill(background_color)
    pygame.draw.polygon(game, white, [(0, 0), (game_width, 0), (0, game_height)])
    pygame.draw.polygon(game, blue, [(game_width, game_height), (game_width, 0), (0, game_height)])
    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    
    # draw labels above the rows
    attack_label = font.render("Select an attacker", True, black)
    attack_rect = attack_label.get_rect(center=(game_width // 2, 50))
    game.blit(attack_label, attack_rect)

    # adjust size of the Pokémon sprites
    for pokemon in pokemons:
        pokemon.size = 100  # set new size for the Pokémon sprites
        pokemon.set_sprite('front_default')  # reset the sprite to adjust size

    # draw Pokémon selection grid
    for i, pokemon in enumerate(pokemons):
        # set positions for Pokémon based on index
        if i < 3:
            pokemon.x = 50 + i * (pokemon.size + 50)
            pokemon.y = 100
        elif i < 6:
            pokemon.x = 50 + (i - 3) * (pokemon.size + 50)
            pokemon.y = 250
        else:
            pokemon.x = 150 + (i - 6) * (pokemon.size + 200)
            pokemon.y = 400

        # get the rectangle for the Pokémon after setting its position
        rect = pokemon.get_rect()

        # highlight box if mouse is pointing to it
        mouse_cursor = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_cursor):
            pygame.draw.rect(game, light_grey, rect)
        else:
            pygame.draw.rect(game, grey, rect)
        
        pygame.draw.rect(game, black, rect, 2)

        # draw Pokémon sprite
        pokemon.draw()

        # draw Pokémon name
        name_text = font.render(pokemon.name, True, black)
        name_rect = name_text.get_rect(center=(pokemon.x + pokemon.image.get_width() // 2, pokemon.y + pokemon.image.get_height() + 17))
        game.blit(name_text, name_rect)
        
        # create the button to return to main menu
        button_main_menu = create_button(150, 50, 20, 425, 95, 450, 'Main Menu')
        
        # create the button to display pokemon stats
        button_stats = create_button(150, 50, 330, 425, 405, 450, 'Stats')

    pygame.display.update()
    return button_main_menu, button_stats

# global variable to keep track of the current Pokémon being displayed
current_pokemon_index = 0

def draw_pokemon_stats_screen(pokemons, index):
    game.fill(background_color)
    pygame.draw.polygon(game, light_orange, [(0, 0), (game_width, 0), (0, game_height)])
    pygame.draw.polygon(game, white, [(game_width, game_height), (game_width, 0), (0, game_height)])
    font = pygame.font.Font(pygame.font.get_default_font(), 20)

    # title
    title = font.render("Pokemon Stats", True, black)
    title_rect = title.get_rect(center=(game_width // 2, 30))
    game.blit(title, title_rect)

    # draw stats for the current Pokémon
    pokemon = pokemons[index]
    pokemon_details = [
        f"Name: {pokemon.name}",
        f"Type: {pokemon.type}",
        f"HP: {pokemon.current_hp}/{pokemon.max_hp}",
        f"Attack: {pokemon.attack}",
        f"Defense: {pokemon.defense}",
        f"Vampirism: {pokemon.vampirism}",
        f"Poison: {pokemon.poison}"
    ]
    
    # draw the Pokémon image
    pokemon_image = pygame.transform.scale(pokemon.image, (300, 300))
    game.blit(pokemon_image, (game_width - 300, 100))

    # draw the Pokémon name and stats
    y = 90
    for detail in pokemon_details:
        text = font.render(detail, True, black)
        text_rect = text.get_rect(left=50, top=y)
        game.blit(text, text_rect)
        y += 30

    # draw Next and Previous buttons
    button_previous = create_button(100, 50, 20, 400, 70, 425, 'Previous')
    button_next = create_button(100, 50, 380, 400, 430, 425, 'Next')

    # back button
    pygame.draw.rect(game, white, (150, 400, 200, 50))
    pygame.draw.rect(game, black, (150, 400, 200, 50), 2)
    text = font.render("Press 'B' to go back", True, black)
    text_rect = text.get_rect(center=(game_width // 2, 425))
    game.blit(text, text_rect)

    pygame.display.update()
    return button_previous, button_next
    
# create the starter pokemons
gallade = Pokemon('Gallade', 'Psychic | Fighting', 25, 50, 55, 5, 0, 0, 0)
rapidash = Pokemon('Rapidash', 'Fire', 175, 50, 45, 7, 0, 0, 0)
aggron = Pokemon('Aggron', 'Steel | Rock', 325, 50, 60, 3, 2, 0, 0)
gliscor = Pokemon('Gliscor', 'Ground | Flying', 25, 200, 40, 4, 0, 0.5, 0)
escavalier = Pokemon('Escavalier', 'Bug | Steel', 175, 200, 50, 6, 0, 0, 0)
gengar = Pokemon('Gengar', 'Ghost | Poison', 325, 200, 45, 4, 0, 0, 2)
pokemons = [gallade, rapidash, aggron, gliscor, escavalier, gengar]

# the player's and rival's selected pokemon
player_pokemon = None
rival_pokemon = None

# game loop
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
            
        # detect keypress
        if event.type == KEYDOWN:
            
            # play again
            if event.key == K_y and game_status == 'gameover':
                # reset the pokemons
                gallade = Pokemon('Gallade', 'Psychic | Fighting', 25, 50, 55, 5, 0, 0, 0)
                rapidash = Pokemon('Rapidash', 'Fire', 175, 50, 45, 7, 0, 0, 0)
                aggron = Pokemon('Aggron', 'Steel | Rock', 325, 50, 60, 3, 2, 0, 0)
                gliscor = Pokemon('Gliscor', 'Ground | Flying', 25, 200, 40, 4, 0, 0.5, 0)
                escavalier = Pokemon('Escavalier', 'Bug | Steel', 175, 200, 50, 6, 0, 0, 0)
                gengar = Pokemon('Gengar', 'Ghost | Poison', 325, 200, 45, 4, 0, 0, 2)
                pokemons = [gallade, rapidash, aggron, gliscor, escavalier, gengar]
                game_status = 'select pokemon'
                
            # quit
            elif event.key == K_n:
                game_status = 'quit'
            
            # back to main menu from instructions
            elif event.key == K_b and game_status == 'instructions':
                game_status = 'main menu'
                
            # back to pokemon selection from stats screen
            elif event.key == K_b and game_status == 'pokemon stats':
                game_status = 'select pokemon'
            
        # detect mouse click
        if event.type == MOUSEBUTTONDOWN:
            
            # coordinates of the mouse click
            mouse_click = event.pos
            
            if game_status == 'main menu':
                if instructions_button.collidepoint(mouse_click):
                    game_status = 'instructions'
                elif play_button.collidepoint(mouse_click):
                    game_status = 'select pokemon'  
                    
            # for selecting a pokemon
            elif game_status == 'select pokemon':
                
                if button_main_menu and button_main_menu.collidepoint(mouse_click):
                    game_status = 'main menu'
                
                elif button_stats and button_stats.collidepoint(mouse_click):
                    game_status = 'pokemon stats'
                    
                # check which pokemon was clicked on
                for i in range(len(pokemons)):
                    
                    if pokemons[i].get_rect().collidepoint(mouse_click):
                        
                        # assign the player's and rival's pokemon
                        player_pokemon = pokemons[i]
                        rival_pokemon = random.choice(pokemons)  # randomly select rival's Pokemon
                        
                        # ensure the player's and rival's Pokémon are different
                        while rival_pokemon == player_pokemon:
                            rival_pokemon = random.choice(pokemons)
                        
                        # set the coordinates of the hp bars
                        player_pokemon.hp_x = 225
                        player_pokemon.hp_y = 275
                        rival_pokemon.hp_x = 100
                        rival_pokemon.hp_y = 50
                        
                        game_status = 'prebattle'
            
            # for selecting attack or using potion
            elif game_status == 'player turn':
                
                # check if attack button was clicked
                if attack_button.collidepoint(mouse_click):
                    player_pokemon.perform_attack(rival_pokemon)
                    
                    # check if the rival's pokemon fainted
                    if rival_pokemon.current_hp == 0:
                        game_status = 'fainted'
                    else:
                        game_status = 'rival turn'
                    
                # check if potion button was clicked
                if potion_button.collidepoint(mouse_click):
                    
                    # force to attack if there are no more potions
                    if player_pokemon.num_potions == 0:
                        display_message('No more potions left!')
                        time.sleep(2)
                        game_status = 'player turn'
                    else:
                        player_pokemon.use_potion()
                        display_message(f'{player_pokemon.name} used a potion!')
                        time.sleep(2)
                        game_status = 'rival turn'   
                                  
            # handle next and previous buttons in stats screen
            elif game_status == 'pokemon stats':
                if button_previous and button_previous.collidepoint(mouse_click):
                    current_pokemon_index = (current_pokemon_index - 1) % len(pokemons)
                elif button_next and button_next.collidepoint(mouse_click):
                    current_pokemon_index = (current_pokemon_index + 1) % len(pokemons)
    
    if game_status == 'main menu':
        instructions_button, play_button = draw_main_menu()

    elif game_status == 'instructions':
        draw_instructions()
        
    # pokemon select screen
    elif game_status == 'select pokemon':
        button_main_menu, button_stats = draw_pokemon_select_screen(pokemons)
    
    # display pokemon stats screen
    elif game_status == 'pokemon stats':
        button_previous, button_next = draw_pokemon_stats_screen(pokemons, current_pokemon_index)
        
    # get moves from the API and reposition the pokemons
    elif game_status == 'prebattle':
        
        # draw the selected pokemon
        game.fill(white)
        player_pokemon.draw()
        pygame.display.update()
        
        # reposition the pokemons
        player_pokemon.x = 0
        player_pokemon.y = 150
        rival_pokemon.x = 300
        rival_pokemon.y = 25
        
        # resize the sprites
        player_pokemon.size = 200
        rival_pokemon.size = 200
        player_pokemon.set_sprite('back_default')
        rival_pokemon.set_sprite('front_default')
        
        game_status = 'start battle'
        
    # start battle animation
    elif game_status == 'start battle':
        
        # rival sends out their pokemon    
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
        
        # player sends out their pokemon
        alpha = 0
        while alpha < 255:
            player_pokemon.draw(alpha, draw_grass_pad=True)
            display_message(f'Go {player_pokemon.name}!')
            alpha += .4 
            pygame.display.update()
        
        # draw the hp bars
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # player goes first
        game_status = 'player turn'
            
        pygame.display.update()
        
        # pause for 1 second
        time.sleep(1)
        
    # display the attack and use potion buttons
    elif game_status == 'player turn':
        
        game.fill(combat_background_grass_color)
        pygame.draw.rect(game, combat_background_sky_color, (0, 0, game_width, 150))
        player_pokemon.draw(draw_grass_pad=True)
        rival_pokemon.draw(draw_grass_pad=True)
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # create the attack and use potion buttons
        attack_button = create_button(240, 140, 10, 350, 130, 420, 'Attack')
        potion_button = create_button(240, 140, 250, 350, 375, 420, f'Potion ({player_pokemon.num_potions})')

        # draw the black border
        pygame.draw.line(game, black, (250, 350), (250, 490), 3)
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
        
        pygame.display.update()
        
    # display the move buttons
    elif game_status == 'player move':
        
        game.fill(combat_background_grass_color)
        pygame.draw.rect(game, combat_background_sky_color, (0, 0, game_width, 250))
        player_pokemon.draw(draw_grass_pad=True)
        rival_pokemon.draw(draw_grass_pad=True)
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # draw the black border
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
        
        pygame.display.update()
        
    # rival selects a random move to attack with
    elif game_status == 'rival turn':
        
        game.fill(combat_background_grass_color)
        pygame.draw.rect(game, combat_background_sky_color, (0, 0, game_width, 150))
        player_pokemon.draw(draw_grass_pad=True)
        rival_pokemon.draw(draw_grass_pad=True)
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # empty the display box and pause for 2 seconds before attacking
        display_message('')
        time.sleep(2)

        # rival decides to attack or use a potion
        if rival_pokemon.current_hp < 20 and rival_pokemon.num_potions > 0:
            rival_pokemon.use_potion()
            display_message(f'{rival_pokemon.name} used a potion!')
            pygame.display.update()  
            time.sleep(2) 
        else:
            # attack player
            rival_pokemon.perform_attack(player_pokemon)
        
        # check if the player's pokemon fainted
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