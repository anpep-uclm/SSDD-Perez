#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
    Game base and states
'''


import uuid

import pyxel

import game.pyxeltools
from game.common import LIFE, LEVEL_COUNT

class GameState:
    '''Game state base class'''
    def __init__(self, parent=None):
        self.parent = parent

    def wake_up(self):
        '''Executed when state begins'''
        pass

    def suspend(self):
        '''Executed when state ends'''
        pass

    def update(self):
        '''Game loop iteration'''
        pass

    def render(self):
        '''Draw single frame'''
        pass

    def go_to_state(self, new_state):
        '''Go to next state of the game'''
        self.parent.enter_state(new_state)


class PlayerData:
    '''Store player data accross the states of the game'''
    def __init__(self, hero_class, steer='Player1', initial_attributes=None):
        self.attribute = {
            'hero_class': hero_class,
            'steer_id': steer,
            LEVEL_COUNT: 1
        }
        if initial_attributes:
            self.attribute.update(initial_attributes)
    
    @property
    def hero_class(self):
        return self.attribute['hero_class']

    @property
    def steer_id(self):
        return self.attribute['steer_id']


class DungeonMap:
    '''Store a list of rooms'''
    def __init__(self, levels):
        self._levels_ = levels
        self._levels_.reverse()

    @property
    def next_room(self):
        if self._levels_:
            return self._levels_.pop()

    @property
    def finished(self):
        return not self._levels_


class Game:
    '''This class wraps the game loop created by pyxel'''
    def __init__(self, hero_class, dungeon):
        self._identifier_ = str(uuid.uuid4())
        self._states_ = {}
        self._current_state_ = None
        self._player_ = PlayerData(hero_class)
        self._dungeon_ = dungeon

    @property
    def identifier(self):
        '''Game unique identifier'''
        return self._identifier_

    @property
    def player(self):
        '''Player data'''
        return self._player_

    @property
    def dungeon(self):
        '''Dungeon data'''
        return self._dungeon_

    def start(self):
        '''Start pyxel game loop'''
        game.pyxeltools.run(self)

    def add_state(self, game_state, identifier):
        '''Add new state to the game'''
        self._states_[identifier] = game_state
        if self._current_state_ is None:
            self.enter_state(identifier)

    def enter_state(self, new_state):
        '''Change game state'''
        if new_state not in self._states_:
            raise ValueError('Unknown state: "{}"'.format(new_state))
        if self._current_state_ is not None:
            self._current_state_.suspend()
        self._current_state_ = self._states_[new_state](self)
        self._current_state_.wake_up()

    def update(self):
        '''Game loop iteration'''
        self._current_state_.update()

    def render(self):
        '''Draw a single frame'''
        self._current_state_.render()
