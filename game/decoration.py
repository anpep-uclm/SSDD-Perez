#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
    Decorations used in the game
'''

from game.game_object import Decoration
from game.sprite import animation
from game.pyxeltools import MAP_ENTITIES
from game.artwork import SMOKE, EXPLOSION


_DECORATIONS_ = {
    'smoke': (4, SMOKE),
    'explosion': (4, EXPLOSION)
}


def new(decoration, position):
    '''Create new decoration object'''
    speed, frames = _DECORATIONS_[decoration]
    return Decoration(animation(MAP_ENTITIES, speed, frames), position)
