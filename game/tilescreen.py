#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
    Tile screen
'''

import pyxel

import game
import game.assets


_TILE_SCR_ = 0


class TileScreen(game.GameState):
    '''A very basic tile screen'''
    _blink_ = 0
    _show_message_ = True
    def wake_up(self):
        game.pyxeltools.load_png_to_image_bank(game.assets.search('tile_screen.png'), _TILE_SCR_)

    def update(self):
        if pyxel.btnr(pyxel.KEY_ENTER):
            self.go_to_next_state()

    def render(self):
        pyxel.blt(0, 0, _TILE_SCR_, 0, 0, pyxel.width, pyxel.height)
        if self._show_message_:
            pyxel.text(90, 220, "PRESS INTRO TO START!", pyxel.COLOR_WHITE)
        self._blink_ += 1
        if self._blink_ > 10:
            self._blink_ = 0
            self._show_message_ = not self._show_message_
