#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
    Game base and states
'''


import uuid

import pyxel

import game.pyxeltools


class GameState:
    '''Game state base class'''
    def __init__(self, parent=None, next_state=None):
        self._parent_ = parent
        self._next_state_ = next_state

    @property
    def next_state(self):
        '''Next state of the game'''
        return self._next_state_

    @next_state.setter
    def next_state(self, new_state):
        '''Change next state'''
        self._next_state_ = new_state

    @property
    def parent_game(self):
        '''Parent game'''
        return self._parent_

    def set_game(self, parent):
        '''Reparent'''
        self._parent_ = parent

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

    def request_state(self, new_state):
        '''Switch to specified game state'''
        self._parent_.enter_state(new_state)

    def go_to_next_state(self):
        '''Go to next state of the game'''
        self.request_state(self.next_state)


class NoState(GameState):
    '''Dummy state of the game'''
    def render(self):
        '''Show warning'''
        pyxel.rect(0, 0, pyxel.width, pyxel.height, pyxel.COLOR_DARKBLUE)
        pyxel.text(10, 20, 'WAITING GAME STATE', pyxel.COLOR_WHITE)


class PlayerData:
    '''Store player data accross the states of the game'''
    def __init__(self, hero_class, steer='Player1', initial_attributes=None):
        self.hero_class = hero_class
        self.steer_id = steer
        self.attribute = initial_attributes or {}


class Game:
    '''This class wraps the game loop created by pyxel'''
    def __init__(self, hero_class):
        self._identifier_ = str(uuid.uuid4())
        self._states_ = {None: NoState(self)}
        self._current_state_ = None
        self._player_ = PlayerData(hero_class)

    @property
    def identifier(self):
        '''Game unique identifier'''
        return self._identifier_

    @property
    def player(self):
        '''Player data'''
        return self._player_

    def start(self):
        '''Start pyxel game loop'''
        game.pyxeltools.run(self)

    def add_state(self, game_state, identifier, switch_to_state=False):
        '''Add new state to the game'''
        self._states_[identifier] = game_state
        self._states_[identifier].set_game(self)
        if switch_to_state:
            self.enter_state(identifier)

    def enter_state(self, new_state):
        '''Change game state'''
        if new_state not in self._states_:
            raise ValueError('Unknown state: "{}"'.format(new_state))
        self._states_[self._current_state_].suspend()
        self._states_[new_state].wake_up()
        self._current_state_ = new_state

    def update(self):
        '''Game loop iteration'''
        self._states_[self._current_state_].update()

    def render(self):
        '''Draw a single frame'''
        self._states_[self._current_state_].render()
