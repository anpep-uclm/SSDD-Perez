#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''Following constants are used by assets images'''


# Warrior
WARRIOR_UP = (0, 8, 16)
WARRIOR_UP_RIGHT = (1, 9, 17)
WARRIOR_RIGHT = (2, 10, 18)
WARRIOR_DOWN_RIGHT = (3, 11, 19)
WARRIOR_DOWN = (4, 12, 20)
WARRIOR_DOWN_LEFT = (5, 13, 21)
WARRIOR_LEFT = (6, 14, 22)
WARRIOR_UP_LEFT = (7, 15, 23)
WARRIOR_EXIT = (24, 25, 26, 27, 28)

# Valkyrie
VALKYRIE_UP = (29, 37, 45)
VALKYRIE_UP_RIGHT = (30, 38, 46)
VALKYRIE_RIGHT = (31, 39, 47)
VALKYRIE_DOWN_RIGHT = (32, 40, 48)
VALKYRIE_DOWN = (33, 41, 49)
VALKYRIE_DOWN_LEFT = (34, 42, 50)
VALKYRIE_LEFT = (35, 43, 51)
VALKYRIE_UP_LEFT = (36, 44, 52)
VALKYRIE_EXIT = (53, 54, 55, 56, 57)

# Wizard
WIZARD_UP = (58, 66, 74)
WIZARD_UP_RIGHT = (59, 67, 75)
WIZARD_RIGHT = (60, 68, 76)
WIZARD_DOWN_RIGHT = (61, 69, 77)
WIZARD_DOWN = (62, 70, 78)
WIZARD_DOWN_LEFT = (63, 71, 79)
WIZARD_LEFT = (64, 72, 80)
WIZARD_UP_LEFT = (65, 73, 81)
WIZARD_EXIT = (82, 83, 84, 85, 86)

# Elf
ELF_UP = (87, 95, 103)
ELF_UP_RIGHT = (88, 96, 104)
ELF_RIGHT = (89, 97, 105)
ELF_DOWN_RIGHT = (90, 98, 106)
ELF_DOWN = (91, 99, 107)
ELF_DOWN_LEFT = (92, 100, 108)
ELF_LEFT = (93, 101, 109)
ELF_UP_LEFT = (94, 102, 110)
ELF_EXIT = (111, 112, 113, 114, 115)

# Smoke
SMOKE = (41, 42, 43)
EXPLOSION = (109, 110, 111)

# Items
TREASURE_ANIM = (121, 122, 123)
TELEPORT_ANIM = (38, 39, 40)

## Following IDs are CELLS not TILES!! ##

CELLS_PER_ROW = 32 # Defined in pyxeltools but not used due to a circular import

# Block cell: list of cells with walls
BLOCK_CELLS = list(range(64))

# Null cell: does not have any graphic at all
NULL_CELL = 990
NULL_CELLS = [NULL_CELL, NULL_CELL + 1, NULL_CELL + CELLS_PER_ROW, NULL_CELL + CELLS_PER_ROW + 1]
NULL_CELLS += list(range(640, 1024))
