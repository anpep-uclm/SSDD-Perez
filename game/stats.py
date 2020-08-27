#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
    Stats screen
'''

import pyxel

import game
import game.assets


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
            self.go_to_next_state()

    def render(self):
        pyxel.rect(0, 0, pyxel.width, pyxel.height, pyxel.COLOR_BLACK)
        pyxel.blt(self.h_center, 10, _TILE_SCR_, 0, 0, *self.tile_resolution)
        if self._show_message_:
            pyxel.text(80, 220, "PRESS INTRO TO CONTINUE!", pyxel.COLOR_WHITE)
        self._blink_ += 1
        if self._blink_ > 10:
            self._blink_ = 0
            self._show_message_ = not self._show_message_
