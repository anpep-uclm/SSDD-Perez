#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
    Tools for pyxel
'''

import json
import logging
import os.path

import pyxel
from PIL import Image

import game.assets
from game.artwork import NULL_CELL


# Pyxel native tile size
CELL_SIZE = 8
# Artwork tile size
TILE_SIZE = 16

MAX_MAP_WIDTH = 256
MAX_MAP_HEIGHT = 256
MAX_MAP_SIZE = (MAX_MAP_WIDTH, MAX_MAP_HEIGHT)

BYTES_PER_COLOR = 3

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 256
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

CELLS_PER_ROW = int(SCREEN_WIDTH / CELL_SIZE)
TILES_PER_ROW = int(SCREEN_WIDTH / TILE_SIZE)

# Used image banks by the engine
#
MAP_ENTITIES = 0
ENEMIES = 1
HEROES = 2

# Used tilemaps by the engine
#
FLOOR_TILEMAP = 0
DECORATION_TILEMAP = 1

# Palette related
#
DEFAULT_PALETTE = [
    0x000100, 0x002985, 0xc20326, 0x842600, 0x694026, 0xff00fd, 0x006900, 0x0069ee,
    0x0769fd, 0xff6700, 0x00c304, 0x15a9fb, 0xff8068, 0xffff00, 0xfdfffc
]
DEFAULT_COLOR_MASK = 5
_CURRENT_COLOR_CONFIG_ = {
    'palette': DEFAULT_PALETTE,
    'color_mask': DEFAULT_COLOR_MASK
}


def assert_valid_tilemap_bank(bank_id):
    '''Check if tilemap id is valid'''
    if bank_id not in range(pyxel.TILEMAP_BANK_COUNT):
        raise ValueError('Invalid tilemap bank: {}'.format(bank_id))


def assert_valid_image_bank(bank_id):
    '''Check if image bank id is valid'''
    if bank_id not in range(pyxel.IMAGE_BANK_FOR_SYSTEM):
        raise ValueError('Invalid image bank: {}'.format(bank_id))


def initialize(title='IceDungeon'):
    '''Initialize pyxel'''
    load_color_config(game.assets.search('palette.json'))
    pyxel.init(*SCREEN_SIZE, caption=title, palette=get_palette())


def run(game_app):
    '''Start pyxel game loop'''
    pyxel.run(game_app.update, game_app.render)


def tile(tile_id):
    '''Return box of 16x16 pixels: (xo, yo, width, height)'''
    y = int(tile_id / TILE_SIZE)
    x = tile_id % TILE_SIZE
    return (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)


def load_png_to_image_bank(image_file, bank):
    '''Load PNG file to a image bank'''
    assert_valid_image_bank(bank)
    image = Image.open(image_file)
    if (image.width > SCREEN_WIDTH) or (image.height > SCREEN_HEIGHT):
        raise ValueError(
            'Image cannot be greater than {}x{} pixels'.format(SCREEN_WIDTH, SCREEN_HEIGHT)
        )

    for y in range(image.height):
        for x in range(image.width):
            pyxel.image(bank).set(x, y, image.getpixel((x, y)))
    return (image.width, image.height)


def clear_tilemap(tilemap_id):
    '''Fill with NULL_CELL a entire tilemap bank'''
    assert_valid_tilemap_bank(tilemap_id)
    for x in range(MAX_MAP_WIDTH):
        for y in range(MAX_MAP_HEIGHT):
            pyxel.tilemap(tilemap_id).set(x, y, NULL_CELL)


def load_json_map(jsonfile):
    '''
        Load JSON file with a map into a pyxel tilemap bank.
        Also support parse the content of the file passed as string
        Return a list of objects in the map.
    '''
    try:
        src_map = json.loads(jsonfile)
    except json.JSONDecodeError:
        logging.debug('Cannot parse JSON data, trying as filename')
        jsonfile = game.assets.search(jsonfile)
        if not jsonfile:
            raise ValueError('JSON file not found!')
        with open(jsonfile, 'r') as contents:
            try:
                src_map = json.load(contents)
            except Exception as error:
                raise ValueError('Wrong JSON data: {}'.format(error))

    map_data = src_map.get('data', None)
    map_name = src_map.get('room', os.path.basename(jsonfile))
    if not map_data:
        raise ValueError('JSON file does not have a data field')
    return map_name, map_data


def put_tile(layer_id, tile_id, position):
    '''Put a "16 pixel sized" tiled into a "8 pixel sized" tilemap'''
    assert_valid_tilemap_bank(layer_id)
    x = (tile_id % TILES_PER_ROW) * 2
    y = int(tile_id / TILES_PER_ROW) * 2
    for y_ofs in [0, 1]:
        for x_ofs in [0, 1]:
            cell_id = ((y + y_ofs) * CELLS_PER_ROW) + (x + x_ofs)
            pyxel.tilemap(layer_id).set(position[0] + x_ofs, position[1] + y_ofs, cell_id)


def load_color_config(color_config_file):
    '''Load color config from JSON file'''
    global _CURRENT_COLOR_CONFIG_
    with open(color_config_file, 'r') as contents:
        loaded_config = json.load(contents)
    loaded_config = {
        'palette': _translate_palette_(loaded_config.get('palette', [])),
        'color_mask': int(loaded_config.get('color_mask', DEFAULT_COLOR_MASK))
    }
    _CURRENT_COLOR_CONFIG_.update(loaded_config)


def get_palette():
    '''Get palette'''
    return _CURRENT_COLOR_CONFIG_.get('palette', DEFAULT_PALETTE)


def get_color_mask():
    '''Get color mask'''
    return _CURRENT_COLOR_CONFIG_.get('color_mask', DEFAULT_COLOR_MASK)


def _translate_palette_(colors):
    translated_palette = []
    for color in colors:
        if isinstance(color, str):
            # Assume WEB format in RGB
            translated_palette.append(int('0x{}'.format(color), 16))
        elif isinstance(color, int):
            translated_palette.append(color)
        else:
            raise ValueError('Unknown color value: {}'.format(color))
    return translated_palette
