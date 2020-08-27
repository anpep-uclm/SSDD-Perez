#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''Game objects bodies'''


from game.pyxeltools import CELL_SIZE
from game.common import X, Y


class Body:
    '''Base class of game objects body'''
    def __init__(self):
        self._game_object_ = None

    @property
    def game_object(self):
        '''Get owner of the body'''
        return self._game_object_

    def set_game_object(self, game_object):
        '''Set the GameObject() owner of this body'''
        self._game_object_ = game_object

    @property
    def size(self):
        '''Size of body in pixels'''
        raise NotImplementedError()

    @property
    def width(self):
        '''Width in pixels of the body'''
        return self.size[0]

    @property
    def height(self):
        '''Height in pixels of the body'''
        return self.size[1]

    def collides_with(self, other_game_object):
        '''Check if one game object collides with other'''
        raise NotImplementedError()

    def ground_fit(self):
        '''Return if body fits on block/door maps'''
        raise NotImplementedError()


class Box(Body):
    '''A simple box with a fixed size in pixels'''
    def __init__(self, size=(0, 0)):
        super(Box, self).__init__()
        self._size_ = size

    @property
    def size(self):
        return self._size_

    def set_game_object(self, game_object):
        super(Box, self).set_game_object(game_object)
        self._size_ = game_object.size

    def collides_with(self, other_game_object):
        if not other_game_object.body:
            return False
        inc_x = self.game_object.attribute[X] - other_game_object.attribute[X]
        inc_y = self.game_object.attribute[Y] - other_game_object.attribute[Y]
        return (
            (abs(inc_x) * 2) < (self.width + other_game_object.body.width)
            and
            (abs(inc_y) * 2) < (self.height + other_game_object.body.height)
        )

    def ground_fit(self):
        # Get borders
        x0 = int(self.game_object.attribute[X] / CELL_SIZE)
        x1 = int((self.game_object.attribute[X] + self._size_[0] - 1) / CELL_SIZE)
        y0 = int(self.game_object.attribute[Y] / CELL_SIZE)
        y1 = int((self.game_object.attribute[Y] + self._size_[1] - 1) / CELL_SIZE)
        # Get blocks at borders
        try:
            collides = {
                self.game_object.room.block[y0][x0], self.game_object.room.block[y0][x1],
                self.game_object.room.block[y1][x0], self.game_object.room.block[y1][x1]
            }
        except IndexError:
            # This error is caused by out-of-map coordinate
            collides = {True}
        # Doors are not boolean blocks
        doors = collides.difference({True, False})
        for door in doors:
            self.game_object.room.send_event(
                ('collision', self.game_object.identifier, door)
            )
        return (not True in collides) and (not doors)
