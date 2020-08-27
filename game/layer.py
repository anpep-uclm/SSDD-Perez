#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
    TileMap handling
'''

import pyxel

from game.common import EMPTY_TILE, AVAILABLE_OBJECT_IDS, NULL_TILE, WALL_TILES
from game.pyxeltools import SCREEN_SIZE, TILE_SIZE, CELL_SIZE, FLOOR_TILEMAP, DECORATION_TILEMAP,\
    clear_tilemap, put_tile


_SHADOW_ = [
    EMPTY_TILE, EMPTY_TILE + 1, EMPTY_TILE + 2, EMPTY_TILE + 3,
    EMPTY_TILE + 4, EMPTY_TILE + 5, EMPTY_TILE + 6, EMPTY_TILE + 5
]


class TileMapLayer:
    '''A simple TileMap layer wrapper class'''
    def __init__(self, tilemap_data, mask):
        self._data_ = tilemap_data
        self._mask_ = mask
        self._objects_ = []
        self._compute_walls_()
        self._compute_shadows_()

    @property
    def objects(self):
        '''List of objects to be spawn on the level'''
        return self._objects_

    def _compute_walls_(self):
        clear_tilemap(FLOOR_TILEMAP)
        y = 0
        for row in self._data_:
            x = 0
            for src_tile in row:
                if src_tile in AVAILABLE_OBJECT_IDS:
                    self._objects_.append((src_tile, (x * TILE_SIZE, y * TILE_SIZE)))
                    src_tile = EMPTY_TILE
                if src_tile == NULL_TILE:
                    src_tile = EMPTY_TILE
                put_tile(FLOOR_TILEMAP, src_tile, (x * 2, y * 2))
                x += 1
            y += 1
        # Convert tiles to cells
        self._map_width_, self._map_height_ = x * 2, y * 2

    def _compute_shadows_(self):
        clear_tilemap(DECORATION_TILEMAP)
        tiles_width, tiles_height = int(self.map_width / 2), int(self.map_height / 2)
        for y in range(1, tiles_height - 1):
            for x in range(1, tiles_width - 1):
                wall_1 = 1 if self._data_[y][x - 1] in WALL_TILES else 0
                wall_2 = 1 if self._data_[y + 1][x - 1] in WALL_TILES else 0
                wall_3 = 1 if self._data_[y + 1][x] in WALL_TILES else 0
                wall_distribution = (4 * wall_3) + (2 * wall_2) + wall_1
                if (wall_distribution == 0) or (self._data_[y][x] in WALL_TILES):
                    continue
                put_tile(DECORATION_TILEMAP, _SHADOW_[wall_distribution], (x * 2, y * 2))

    @property
    def width(self):
        '''Width of the layer in pixels'''
        return self._map_width_ * CELL_SIZE

    @property
    def height(self):
        '''Height of the layer in pixels'''
        return self._map_height_ * CELL_SIZE

    @property
    def size(self):
        '''Size of the layer in pixels'''
        return (self.width, self.height)

    @property
    def map_width(self):
        '''Width of the layer in cells'''
        return self._map_width_

    @property
    def map_height(self):
        '''Height of the layer in cells'''
        return self._map_height_

    @property
    def map_size(self):
        '''Size of the layer in cells'''
        return (self.map_width, self.map_height)

    def get_cell_at(self, x, y):
        '''Get cell data of a given coordinates'''
        if (0 <= x < self.map_width) and (0 <= y < self.map_height):
            return pyxel.tilemap(FLOOR_TILEMAP).get(x, y)
        raise ValueError('position out of the map')

    def set_cell_at(self, x, y, new_value):
        '''Set cell data of a given coordinates'''
        if (0 <= x < self.map_width) and (0 <= y < self.map_height):
            pyxel.tilemap(FLOOR_TILEMAP).set(x, y, new_value)
            return
        raise ValueError('position out of the map')

    def render(self, x=0, y=0):
        '''Draw layer'''
        pyxel.rect(0, 0, *SCREEN_SIZE, self._mask_)
        pyxel.bltm(x, y, FLOOR_TILEMAP, 0, 0, self._map_width_, self._map_height_, self._mask_)
        pyxel.bltm(x, y, DECORATION_TILEMAP, 0, 0, self._map_width_, self._map_height_, self._mask_)
