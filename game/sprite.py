#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
2D graphics
'''

import pyxel

from game.pyxeltools import tile, get_color_mask


class Drawable:
    '''A object that can be drawed into screen'''
    def render(self, x=0, y=0):
        '''How to render the object'''
        raise NotImplementedError()

    @property
    def width(self):
        '''Width in pixels'''
        raise NotImplementedError()

    @property
    def height(self):
        '''Height in pixels'''
        raise NotImplementedError()

    @property
    def size(self):
        '''Size in pixels'''
        return (self.width, self.height)

    def set_paused(self, paused):
        '''Only used in animations'''
        pass

    @property
    def ended(self):
        '''On Animations this should be redefined'''
        return False


class Raster(Drawable):
    '''A sprite made by single raster'''
    def __init__(self, image_bank_id, x, y, width, height):
        self._bank_ = image_bank_id
        self._xo_ = x
        self._yo_ = y
        self._height_ = width
        self._width_ = height
        self._mask_ = get_color_mask()

    @property
    def width(self):
        '''Width in pixels'''
        return self._width_

    @property
    def height(self):
        '''Height in pixels'''
        return self._height_

    def render(self, x=0, y=0):
        '''Draw picture on a given position (using pixel mask)'''
        pyxel.blt(x, y, self._bank_, self._xo_, self._yo_, self._width_, self._height_, self._mask_)


class Animation(Drawable):
    '''A sequence of sprites'''
    def __init__(self, loop=False, ticks_per_frame=20, *frames):
        self._frames_ = list(frames)
        self._loop_ = loop
        self._paused_ = False
        self._tpf_ = ticks_per_frame

        self._current_frame_ = 0
        self._current_tick_ = 0
        self._last_frame_ = len(self._frames_) - 1
        self._width_ = max([frame.width for frame in self._frames_])
        self._height_ = max([frame.height for frame in self._frames_])

    @property
    def width(self):
        '''Width in pixels'''
        return self._width_

    @property
    def height(self):
        '''Height in pixels'''
        return self._height_

    @property
    def ended(self):
        '''Returns if animation is ended'''
        return False if self._loop_ else (self._current_frame_ == self._last_frame_)

    def reset(self):
        '''Restart animation'''
        self._current_frame_ = 0
        self._current_tick_ = 0
        self._paused_ = False

    def set_paused(self, paused):
        '''Pause/continue animation'''
        self._paused_ = paused

    def render(self, x=0, y=0):
        '''Draw animation on a given position'''
        self._frames_[self._current_frame_].render(x, y)
        if not self.ended and not self._paused_:
            self._current_tick_ += 1
            if self._current_tick_ > self._tpf_:
                self._current_tick_ = 0
                self._current_frame_ += 1
                if self._current_frame_ > self._last_frame_:
                    self._current_frame_ = 0 if self._loop_ else self._last_frame_

# Factories
def loop_animation(image_bank, speed, frame_ids):
    '''Create a new infinite animation from given image_bank and tiles'''
    frames = []
    for frame_id in frame_ids:
        frames.append(Raster(image_bank, *tile(frame_id)))
    return Animation(True, speed, *frames)

def animation(image_bank, speed, frame_ids):
    '''Create a one-shot animation from given image_bank and tiles'''
    frames = []
    for frame_id in frame_ids:
        frames.append(Raster(image_bank, *tile(frame_id)))
    return Animation(False, speed, *frames)
