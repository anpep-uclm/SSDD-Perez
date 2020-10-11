#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''Common definitions used in project'''

# Scoring
POINTS_PER_DOOR = 40
POINTS_PER_KEY = 100
POINTS_PER_LEVEL = 200
#POINTS_PER_TREASURE = <random>

# Attributes
X = 'x'
Y = 'y'
DIR_X = 'dir_x'
DIR_Y = 'dir_y'
SPEED = 'speed'
HERO_CLASS = 'class'
TAGS = 'tags'
TILE_ID = 'tile_id'
KEYS = 'keys'
SCORE = 'score'
LIFE = 'life'
LEVELS = 'levels'
LEVEL_COUNT = 'level_count'

# Map entities #

# Walls
WALL_TILES = list(range(0, 16))

# Doors
DOORS = list(range(19, 34))

# Key
KEY = 119
OSD_KEY = KEY + 29

# Treasure
TREASURE = 121

# Food
JAR = 113
HAM = 116

# Exit
EXIT = 101

# Teleport
TELEPORT = 38

# Special tiles
EMPTY_TILE = 48
NULL_TILE = 255

# Spawns
DEFAULT_SPAWN = 250
WARRIOR_SPAWN = DEFAULT_SPAWN + 1
VALKYRIE_SPAWN = DEFAULT_SPAWN + 2
WIZARD_SPAWN = DEFAULT_SPAWN + 3
ELF_SPAWN = DEFAULT_SPAWN + 4
SPAWN_IDS = [DEFAULT_SPAWN, WARRIOR_SPAWN, VALKYRIE_SPAWN, WIZARD_SPAWN, ELF_SPAWN]

AVAILABLE_OBJECT_IDS = [KEY, TREASURE, EXIT, TELEPORT, HAM, JAR] + DOORS + SPAWN_IDS

# Actors #

# Heroes
INITIAL_HERO_LIFE = 300
WARRIOR = 'warrior'
VALKYRIE = 'valkyrie'
WIZARD = 'wizard'
ELF = 'elf'
HEROES = [WARRIOR, VALKYRIE, WIZARD, ELF]
HEROES_SPAWN = {
    WARRIOR: WARRIOR_SPAWN,
    VALKYRIE: VALKYRIE_SPAWN,
    WIZARD: WIZARD_SPAWN,
    ELF: ELF_SPAWN
}

# Game states #
INITIAL_SCREEN = 'initial_screen'
STATUS_SCREEN = 'stats_screen'
GAME_SCREEN = 'game_screen'
GAME_OVER_SCREEN = 'gameover_screen'
GOOD_END_SCREEN = 'goodend_screen'
