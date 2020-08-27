#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
    Steers implementation
'''

import pyxel

from game.common import DIR_X, DIR_Y


_ANIM_ = {
    -1: {
        -1: 'up_left',
        0: 'left',
        1: 'down_left'
    },
    0: {
        -1: 'up',
        0: 'stand_by',
        1: 'down'
    },
    1: {
        -1: 'up_right',
        0: 'right',
        1: 'down_right'
    }
}


class Steer:
    '''This object control any Actor()'''
    def __init__(self, actor=None):
        self.actor = actor

    def update(self):
        '''Run a game loop iteration'''
        raise NotImplementedError()


class Static(Steer):
    '''This steer does nothing'''
    def update(self):
        self.actor.reset()


class Player1(Steer):
    '''This steer allows to control an actor with keyboard'''
    last_dir_x = 0
    last_dir_y = 0
    def update(self):
        if self.actor.state == 'exit':
            self.actor.attribute[DIR_X] = self.actor.attribute[DIR_Y] = 0
            return

        if pyxel.btn(pyxel.KEY_LEFT):
            self.actor.attribute[DIR_X] = -1
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.actor.attribute[DIR_X] = 1
        else:
            self.actor.attribute[DIR_X] = 0

        if pyxel.btn(pyxel.KEY_UP):
            self.actor.attribute[DIR_Y] = -1
        elif pyxel.btn(pyxel.KEY_DOWN):
            self.actor.attribute[DIR_Y] = 1
        else:
            self.actor.attribute[DIR_Y] = 0

        if ((self.last_dir_x != self.actor.attribute[DIR_X]) or
                (self.last_dir_y != self.actor.attribute[DIR_Y])):
            if not self.actor.attribute[DIR_X] == self.actor.attribute[DIR_Y] == 0:
                self.actor.state = _ANIM_[self.actor.attribute[DIR_X]][self.actor.attribute[DIR_Y]]
            self.actor.room.send_event(
                ('set_direction', self.actor.identifier,
                 self.actor.attribute[DIR_X], self.actor.attribute[DIR_Y])
            )
        (self.last_dir_x,
         self.last_dir_y) = (self.actor.attribute[DIR_X], self.actor.attribute[DIR_Y])


_STEERS_ = {
    'Player1': Player1
}


def available_steers():
    '''Get list of available steers'''
    return list(_STEERS_.keys())


def new(steer_name):
    '''Steer() factory'''
    if steer_name not in available_steers():
        raise ValueError('Invalid "steer_name": {}'.format(steer_name))
    return _STEERS_[steer_name]
