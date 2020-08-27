#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
    Objects used in the game
'''

from game.artwork import TREASURE_ANIM, TELEPORT_ANIM
from game.game_object import Item
from game.common import X, Y, TILE_ID,\
    KEY, JAR, HAM, TREASURE, EXIT, TELEPORT, DOORS, NULL_TILE,\
    DEFAULT_SPAWN, SPAWN_IDS
from game.sprite import Raster, loop_animation
from game.pyxeltools import tile, MAP_ENTITIES


class Door(Item):
    '''Special item: door'''
    def __init__(self, door_image, position=(0, 0), identifier=None):
        super(Door, self).__init__(door_image, position, identifier)
        self.block_x = self.block_y = 0

    def do_create(self):
        # Anotate door identifier in block map
        self.block_x, self.block_y = int(self.attribute[X] / 8), int(self.attribute[Y] / 8)
        for x_ofs in [0, 1]:
            for y_ofs in [0, 1]:
                self.room.block[self.block_y + y_ofs][self.block_x + x_ofs] = self.identifier

    def do_kill(self):
        # Remove door identifier from block map
        for x_ofs in [0, 1]:
            for y_ofs in [0, 1]:
                self.room.block[self.block_y + y_ofs][self.block_x + x_ofs] = False


class Spawn(Item):
    '''Special item: spawn area'''
    def __init__(self, animation, initial_position=(0, 0), identifier=None, spawn=DEFAULT_SPAWN):
        super(Spawn, self).__init__(animation, initial_position, identifier)
        self.body = None
        self.spawn = spawn


def new(object_id, identifier):
    '''Factory for game items'''
    if object_id in DOORS:
        game_object = Door(Raster(MAP_ENTITIES, *tile(object_id)), identifier=identifier)
    elif object_id in SPAWN_IDS:
        game_object = Spawn(
            Raster(MAP_ENTITIES, *tile(NULL_TILE)), identifier=identifier, spawn=object_id
        )
    elif object_id == TREASURE:
        game_object = Item(loop_animation(MAP_ENTITIES, 3, TREASURE_ANIM), identifier=identifier)
    elif object_id == TELEPORT:
        game_object = Item(loop_animation(MAP_ENTITIES, 3, TELEPORT_ANIM), identifier=identifier)
    else:
        game_object = Item(Raster(MAP_ENTITIES, *tile(object_id)), identifier=identifier)
    game_object.attribute[TILE_ID] = object_id
    return game_object


def new_object(object_id, identifier):
    '''Factory alias'''
    return new(object_id, identifier)
