#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

''' Camera control '''


from game.pyxeltools import SCREEN_WIDTH, SCREEN_HEIGHT


_LERP_FACTOR_ = 0.05
def _lerp_(src, dst):
    return round((1 - _LERP_FACTOR_) * src + _LERP_FACTOR_ * dst)


class Camera:
    '''A Camera for a Room with targetting support'''
    def __init__(self, layer):
        self._center_ = (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2))
        self._target_ = (0, 0)
        self._position_ = (0, 0)
        self._top_ = (
            min(0, -(layer.width - SCREEN_WIDTH)),
            min(0, -(layer.height - SCREEN_HEIGHT))
        )
        self._target_object_ = None

    @property
    def position(self):
        '''Current postion of the camera target in the layer'''
        return self._position_

    def warp_to(self, position):
        '''Move camera target without traveling'''
        self._target_ = position
        self._position_ = (self._center_[0] - position[0], self._center_[1] - position[1])

    def set_target(self, game_object):
        '''Set a new target'''
        self._target_object_ = game_object

    def update(self):
        '''Update camera position'''
        if self._target_object_:
            self._target_ = self._target_object_.position
        self._position_ = (
            max(
                min(0, _lerp_(self._position_[0], self._center_[0] - self._target_[0])),
                self._top_[0]
            ),
            max(
                min(0, _lerp_(self._position_[1], self._center_[1] - self._target_[1])),
                self._top_[1]
            )
        )
