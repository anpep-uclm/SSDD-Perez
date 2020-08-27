#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''Base classes for every in-game object'''


import uuid

from game.bodies import Body, Box
from game.steers import Static
from game.sprite import Drawable
from game.common import X, Y, DIR_X, DIR_Y, SPEED, TAGS

_STANDBY_ = 'stand_by'


class GameObject:
    '''Base of game objects'''
    def __init__(self, initial_position=(0, 0), identifier=None):
        self._id_ = identifier or str(uuid.uuid4())
        self._body_ = None
        self._room_ = None
        self.attribute = {
            X: initial_position[0],
            Y: initial_position[1],
            TAGS: []
        }

    @property
    def identifier(self):
        '''Game object ID'''
        return self._id_

    @property
    def tags(self):
        '''Object tags'''
        return self.attribute[TAGS]

    @property
    def room(self):
        '''Reference to a parent Room()'''
        return self._room_

    def set_attribute(self, attribute_name, value):
        '''Set/create custom attribute'''
        self.attribute[attribute_name] = value

    def get_attribute(self, attribute_name, default=None):
        '''Get custom attribute'''
        return self.attribute.get(attribute_name, default)

    @room.setter
    def room(self, new_room):
        '''Set new room or None to kill object'''
        if new_room is None:
            self.do_kill()
            self._room_ = None
        else:
            self._room_ = new_room
            self.do_create()

    @property
    def acting(self):
        '''GameObject has a Animation() that is currently moving'''
        return False

    @property
    def position(self):
        '''Get current position'''
        return (self.attribute[X], self.attribute[Y])

    @position.setter
    def position(self, new_position):
        '''Set current position'''
        self.attribute[X] = new_position[0]
        self.attribute[Y] = new_position[1]

    def kill(self):
        '''Kill object'''
        if self.room:
            self.room.kill(self)

    @property
    def body(self):
        '''Get the body of the object'''
        return self._body_

    @body.setter
    def body(self, new_body):
        '''Set the body of the object'''
        if (not isinstance(new_body, Body)) and (new_body is not None):
            raise TypeError('"new_body" must be a Body() instance or None')
        self._body_ = new_body
        if self._body_:
            self.body.set_game_object(self)

    def collides_with(self, other_game_object):
        '''Return if other_game_object collides with current GameObject'''
        if (not self.body) or (not other_game_object.body):
            return False
        return self.body.collides_with(other_game_object.body)

    def do_create(self):
        '''This method is called when GameObject is spawned into the room'''
        pass

    def do_kill(self):
        '''This method is called when GameObject is killed'''
        pass

    def update(self):
        '''GameObject iteration'''
        pass

    def render(self, x_offset, y_offset):
        '''Render GameObject with given offset'''
        pass


class Decoration(GameObject):
    '''GameObject with a single animation that is killed as soon as animation ends'''
    def __init__(self, animation, initial_position=(0, 0)):
        super(Decoration, self).__init__(initial_position, identifier=None)
        self._animation_ = animation
        self._animation_.reset()
        self._ready_to_kill_ = False

    @property
    def acting(self):
        return not self._animation_.ended

    def render(self, x_offset=0, y_offset=0):
        if self._ready_to_kill_:
            self.kill()
        self._animation_.render(self.attribute[X] + x_offset, self.attribute[Y] + y_offset)
        self._ready_to_kill_ = not self.acting


class Item(GameObject):
    '''GameObject with one image or animation. Stores a state and a Box body'''
    def __init__(self, animation, initial_position=(0, 0), identifier=None):
        super(Item, self).__init__(initial_position, identifier)
        if not isinstance(animation, (dict, Drawable)):
            raise TypeError('"animation" must be a Drawable() object or a dict')
        if isinstance(animation, Drawable):
            self._animations_ = {'initial': animation}
        else:
            self._animations_ = animation
        if 'initial' not in self._animations_:
            raise ValueError('"initial" animation not provided')
        self._current_state_ = self._current_animation_ = 'initial'

        self._width_ = max([animation.width for animation in self._animations_.values()])
        self._height_ = max([animation.height for animation in self._animations_.values()])
        self.body = Box(self.size)

    @property
    def acting(self):
        return True

    @property
    def width(self):
        '''Width of the GameObject body'''
        return self._width_

    @property
    def height(self):
        '''Heigth of the GameObject body'''
        return self._height_

    @property
    def size(self):
        '''Size of the GameObject body'''
        return (self.width, self.height)

    @property
    def state(self):
        '''Current state of the GameObject'''
        return self._current_state_

    @state.setter
    def state(self, new_state):
        '''Change state of the GameObject'''
        self.set_state(new_state)

    def set_state(self, new_state):
        '''Change state of the GameObject'''
        if new_state in self._animations_:
            self._current_animation_ = new_state
            self.reset_action()
        if not self.room:
            return
        if new_state == self._current_state_:
            return
        self._current_state_ = new_state

    def reset_action(self):
        '''Reset current animation state'''
        self._animations_[self._current_animation_].reset()

    def render(self, x_offset=0, y_offset=0):
        self._animations_[self._current_animation_].render(
            self.attribute[X] + x_offset, self.attribute[Y] + y_offset
        )


class Actor(GameObject):
    '''Game object with state, animations per state, body and Steer'''
    def __init__(self, animations=None, initial_position=(0, 0), identifier=None):
        super(Actor, self).__init__(initial_position, identifier)
        animations = animations or {}
        if isinstance(animations, Drawable):
            self.__anims__ = {_STANDBY_: animations}
        elif isinstance(animations, dict):
            if _STANDBY_ not in animations:
                raise ValueError('Required key "{}" not found in animations'.format(_STANDBY_))
            for animation in animations.values():
                if not isinstance(animation, Drawable):
                    raise TypeError('Value {} is not a Drawable() object!')
            self.__anims__ = animations
        else:
            raise TypeError('"animations" should be a Drawable() object or a dict')

        self.__current_state__ = _STANDBY_
        self.__steer__ = Static(self)
        self.attribute[SPEED] = 2
        self.attribute[DIR_X] = 0
        self.attribute[DIR_Y] = 0

    @property
    def steer(self):
        '''Get the Steer() object'''
        return self.__steer__

    @steer.setter
    def steer(self, new_steer):
        '''Set new Steer()'''
        self.__steer__ = new_steer(self)
        self.reset()

    @property
    def width(self):
        '''Width in pixels'''
        return self.__anims__[self.__current_state__].width

    @property
    def height(self):
        '''Height in pixels'''
        return self.__anims__[self.__current_state__].height

    @property
    def size(self):
        '''Size in pixels'''
        return self.__anims__[self.__current_state__].size

    @property
    def acting(self):
        '''Return if actor is running an animation'''
        return not self.__anims__[self.__current_state__].ended

    def reset_action(self):
        '''Restart current actor animation'''
        self.__anims__[self.__current_state__].reset()

    def reset(self):
        '''Restart actor state'''
        self.state = _STANDBY_

    @property
    def state(self):
        '''Get current actor state'''
        return self.__current_state__

    @state.setter
    def state(self, new_state):
        '''Set actor state (setter)'''
        self.set_state(new_state)

    def set_state(self, new_state):
        '''Set actor state'''
        if new_state not in self.__anims__:
            raise ValueError('Invalid state: {}'.format(new_state))
        if (not self.room) or (new_state == self.__current_state__):
            return
        self.__current_state__ = new_state
        self.reset_action()

    def update(self):
        if not self.room:
            return
        self.__steer__.update()
        self.__anims__[self.__current_state__].set_paused(
            (self.attribute[DIR_X] == self.attribute[DIR_Y] == 0) and
            (self.__current_state__ != 'exit')
        )
        current_position = (self.attribute[X], self.attribute[Y])
        self.attribute[Y] += (self.attribute[SPEED] * self.attribute[DIR_Y])
        if not self.body.ground_fit():
            self.attribute[Y] = current_position[1]
        self.attribute[X] += (self.attribute[SPEED] * self.attribute[DIR_X])
        if not self.body.ground_fit():
            self.attribute[X] = current_position[0]

    def render(self, x_offset=0, y_offset=0):
        self.__anims__[self.__current_state__].render(
            self.attribute[X] + x_offset, self.attribute[Y] + y_offset
        )
