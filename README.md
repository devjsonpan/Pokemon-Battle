# Pokémon Battle Royale ⚡

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-green?style=for-the-badge&logo=pygame&logoColor=white)](https://www.pygame.org/)
[![PokeAPI](https://img.shields.io/badge/PokeAPI-Data-red?style=for-the-badge)](https://pokeapi.co/)

A turn-based Pokémon battle simulator featuring unique status effects, type advantages, and strategic combat. Battle against an AI opponent in this fully-featured GUI game!

## 🎮 Features

### 6 Unique Pokémon
| Pokémon | Type | Special Ability | Weakness |
|---------|------|-----------------|----------|
| Raichu | Electric | Paralysis (50% chance) | Ground |
| Charizard | Fire | Burn (50% chance) | Water |
| Venusaur | Grass | Sleep (75% chance) | Fire |
| Gyarados | Water | Confusion (100% chance) | Electric |
| Nidoking | Ground | Poison (100% chance) | Grass |
| Dragonite | Dragon | None | None |

### Battle Mechanics
- **Type Advantages** - Super effective attacks deal +10 damage
- **Missed Attacks** - 25% chance to miss
- **Healing System** - 2 potions per battle (heals 50 HP + cures status)
- **AI Opponent** - Uses potions strategically when low on health

### Status Effects
| Effect | Damage | Recovery |
|--------|--------|----------|
| Burn | 20 damage/turn | 50% coin flip each turn |
| Poison | 10 damage/turn | Permanent (potion cures) |
| Sleep | Cannot attack | 50% coin flip to wake up |
| Paralysis | Cannot act for 1 turn | Removed after 1 turn |
| Confusion | 50% chance to miss attack | Removed after missed attack |

## 🎯 How to Play

1. **Launch the game** - Run `python pokemon_battle.py`
2. **Select your Pokémon** - Select from any of the 6 options
3. **Battle!**
   - **Attack** - Use your special move
   - **Potion** - Heal 50 HP and cure status (2 per battle)
4. **Win** by reducing opponent's HP to 0

*Turn order is determined by a coin flip at the start of each battle.*

## 📸 Screenshots

<table>
  <tr>
    <td align="center">
      <img width="250" alt="Main Menu" src="https://github.com/user-attachments/assets/7fc3baae-cc86-4cbb-97ee-4e25edfdfced"/>
      <br/><em>Main Menu</em>
    </td>
    <td align="center">
      <img width="250" alt="Pokémon Selection" src="https://github.com/user-attachments/assets/82152af6-ae63-44ed-ac1c-36fc04ba1d47"/>
      <br/><em>Pokémon Selection</em>
    </td>
    <td align="center">
      <img width="250" alt="Stats View" src="https://github.com/user-attachments/assets/661a254b-d526-4bfa-aa37-d68265494ba2"/>
      <br/><em>Battle Screen</em>
    </td>
    <td align="center">
      <img width="250" alt="Battle Screen" src="https://github.com/user-attachments/assets/31a5f914-b26e-4d58-a66b-940327799298"/>
      <br/><em>Stats View</em>
    </td>
  </tr>
</table>

## 🛠️ Built With

- **Pygame** - Game graphics, animations, and event handling
- **PokeAPI** - Pokémon sprites and data
- **Python OOP** - Modular class-based design

## 📁 Project Structure

```
Pokemon-Battle/
├── pokemon_battle.py        # Main game file               
└── README.md                # This file
```
## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/devjsonpan/Pokemon-Battle.git
   cd Pokemon-Battle
   ```

2. **Install pygame**
   ```bash
   pip install pygame
   ```

3. **Run the game**
   ```bash
   python pokemon_battle.py
   ```
**Note:** If you're using a newer version of Python like Python 3.14, Pygame may not be available yet. Use an earlier version of Python instead.
For instance, if you have Python 3.10 installed, run `py -3.10 pokemon_battle.py`

## 📝 Acknowledgements
- This project was inspired by [this tutorial](https://www.youtube.com/watch?v=Qbg2ZunNfJY) and [Pokémon TCG Pocket Status Effects](https://game8.co/games/Pokemon-TCG-Pocket/archives/483132)
