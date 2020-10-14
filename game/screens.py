#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
    In-game screens
'''

import pyxel

import game
import game.assets
from game.common import GAME_SCREEN, STATUS_SCREEN, INITIAL_SCREEN,\
    LEVEL_COUNT, LEVELS

_TILE_SCR_ = 0


class StatsScreen(game.GameState):
    '''A very basic status screen'''
    _blink_ = 0
    _show_message_ = True
    tile_resolution = (0, 0)
    h_center = 0

    def wake_up(self):
        self.tile_resolution = game.pyxeltools.load_png_to_image_bank(
            game.assets.search('tile.png'), _TILE_SCR_
        )
        self.h_center = int((pyxel.width / 2) - (self.tile_resolution[0] / 2))

    def update(self):
        if pyxel.btnr(pyxel.KEY_ENTER):
            self.go_to_state(GAME_SCREEN)

    def render(self):
        pyxel.rect(0, 0, pyxel.width, pyxel.height, pyxel.COLOR_BLACK)
        pyxel.blt(self.h_center, 10, _TILE_SCR_, 0, 0, *self.tile_resolution)
        if self._show_message_:
            pyxel.text(80, 220, "PRESS INTRO TO CONTINUE!", pyxel.COLOR_WHITE)
        self._blink_ += 1
        if self._blink_ > 10:
            self._blink_ = 0
            self._show_message_ = not self._show_message_


class TileScreen(game.GameState):
    '''A very basic tile screen'''
    _blink_ = 0
    _show_message_ = True
    def wake_up(self):
        game.pyxeltools.load_png_to_image_bank(game.assets.search('tile_screen.png'), _TILE_SCR_)
        self.level = self.parent.player.attribute[LEVEL_COUNT]

    def update(self):
        if pyxel.btnr(pyxel.KEY_ENTER):
            self.go_to_state(STATUS_SCREEN)

    def render(self):
        pyxel.blt(0, 0, _TILE_SCR_, 0, 0, pyxel.width, pyxel.height)
        if self._show_message_:
            pyxel.text(90, 220, "PRESS INTRO TO START!", pyxel.COLOR_WHITE)
        self._blink_ += 1
        if self._blink_ > 10:
            self._blink_ = 0
            self._show_message_ = not self._show_message_


class GameOverScreen(game.GameState):
    '''A very basic game over screen'''
    tile_resolution = (0, 0)
    h_center = 0
    timeout = 0

    def wake_up(self):
        self.timeout = 300
        self.tile_resolution = game.pyxeltools.load_png_to_image_bank(
            game.assets.search('tile.png'), _TILE_SCR_
        )
        self.h_center = int((pyxel.width / 2) - (self.tile_resolution[0] / 2))

    def update(self):
        if (pyxel.btnr(pyxel.KEY_ENTER)) or (self.timeout <= 0):
            self.go_to_state(INITIAL_SCREEN)
        self.timeout -= 1

    def render(self):
        pyxel.rect(0, 0, pyxel.width, pyxel.height, pyxel.COLOR_BLACK)
        pyxel.blt(self.h_center, 10, _TILE_SCR_, 0, 0, *self.tile_resolution)
        pyxel.text(80, 220, "GAME OVER", pyxel.COLOR_WHITE)


class GoodEndScreen(game.GameState):
    '''A very basic good end screen'''
    tile_resolution = (0, 0)
    h_center = 0
    timeout = 0

    def wake_up(self):
        self.timeout = 300
        self.tile_resolution = game.pyxeltools.load_png_to_image_bank(
            game.assets.search('tile.png'), _TILE_SCR_
        )
        self.h_center = int((pyxel.width / 2) - (self.tile_resolution[0] / 2))

    def update(self):
        if (pyxel.btnr(pyxel.KEY_ENTER)) or (self.timeout <= 0):
            self.go_to_state(INITIAL_SCREEN)
        self.timeout -= 1

    def render(self):
        pyxel.rect(0, 0, pyxel.width, pyxel.height, pyxel.COLOR_BLACK)
        pyxel.blt(self.h_center, 10, _TILE_SCR_, 0, 0, *self.tile_resolution)
        pyxel.text(80, 220, "GOOD END", pyxel.COLOR_WHITE)


class GameScreen(game.GameState):
    '''Game screen'''
    def __init__(self, parent):
        super(GameScreen, self).__init__(parent)
        room = self.parent.dungeon.next_room
        self.room = game.level.Level(self.parent)
        self.room.orchestrator = game.orchestration.RoomOrchestration(room)

        self.wake_up = self.room.wake_up
        self.suspend = self.room.suspend
        self.update = self.room.update
        self.render = self.room.render        
