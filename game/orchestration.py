#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
Orchestration of game in a dungeon room
'''


import sys
import math
import time
import uuid
import random
import logging

import game.layer
import game.level
import game.heroes
import game.steers
import game.objects
from game.common import DOORS, KEYS, AVAILABLE_OBJECT_IDS, EMPTY_TILE, NULL_TILE,\
    X, Y, TAGS, LIFE, SCORE,\
    POINTS_PER_DOOR, POINTS_PER_KEY, POINTS_PER_LEVEL
from game.pyxeltools import TILE_SIZE, load_json_map


def _closest_(target, objects=None):
    if not objects:
        return None
    current_distance = sys.float_info.max
    closest = None
    for candidate in objects:
        distance = math.sqrt(
            (target.x - target.x) ** 2 + (target.y - candidate.y) ** 2
        )
        if distance < current_distance:
            current_distance = distance
            closest = candidate
    return closest


def _random_arround_(center):
    x, y = int(center[0] / TILE_SIZE), int(center[1] / TILE_SIZE)
    # FIXME: in the worst case this can be an infinite loop!!
    while True:
        x_offset = random.randint(-1, 1)
        y_offset = random.randint(-1, 1)
        if x_offset == y_offset == 0:
            continue
        return ((x + x_offset) * TILE_SIZE, (y + y_offset) * TILE_SIZE)


def __discard_event__(event):
    logging.debug(f'Lost event: {event}')


class TrackedGameObject:
    '''Every game object in the Room() but only data info'''
    def __init__(self, identifier, object_class, object_type, attributes=None):
        attributes = attributes or {}
        self.identifier = identifier
        self.object_class = object_class
        self.object_type = object_type
        self.state = "initial"
        self.attribute = {X: 0, Y: 0}
        self.attribute.update(attributes)

    @property
    def x(self):
        '''Shortcut to horizontal position'''
        return self.attribute[X]

    @property
    def y(self):
        '''Shortcut to vertical position'''
        return self.attribute[Y]

    @property
    def tags(self):
        '''Shortcut to TAGS attribute'''
        return self.attribute.get(TAGS, [])

    @property
    def position(self):
        '''Shortcut to object position attribute'''
        return (self.attribute[X], self.attribute[Y])

    @position.setter
    def position(self, new_position):
        '''Shortcut to set object position'''
        self.attribute[X] = new_position[0]
        self.attribute[Y] = new_position[1]


class RoomOrchestration:
    '''A running game instance'''
    def __init__(self, room):
        self._identifier_ = None
        self._room_ = room
        self._game_objects_ = {}
        self._map_objects_ = []
        self._event_target_ = __discard_event__
        self.parent_level = None
        self._last_time_ = int(time.time())

    @property
    def identifier(self):
        '''Game instance identifier'''
        return self._identifier_

    @identifier.setter
    def identifier(self, new_identifier):
        '''Change game identifier'''
        self._identifier_ = new_identifier

    @property
    def event_target(self):
        '''Get event destination callback'''
        return self._event_target_

    @event_target.setter
    def event_target(self, new_event_target):
        '''Set event destination callback'''
        self._event_target_ = new_event_target

    def start(self):
        '''Start new map'''
        self._game_objects_ = {}
        self._map_objects_ = []
        self._load_map_()
        for object_type, position in self._map_objects_:
            self._spawn_object_(object_type, *position)
        self._spawn_player_()

    @property
    def tracked_objects(self):
        '''Tracked objects'''
        return self._game_objects_

    def _load_map_(self):
        map_name, map_data = load_json_map(self._room_)
        # Get objects and replace by empty tile
        y = 0
        for row in map_data:
            x = 0
            for src_tile in row:
                if src_tile in AVAILABLE_OBJECT_IDS:
                    self._map_objects_.append((src_tile, (x * TILE_SIZE, y * TILE_SIZE)))
                    src_tile = EMPTY_TILE
                if src_tile == NULL_TILE:
                    src_tile = EMPTY_TILE
                map_data[y][x] = src_tile
                x += 1
            y += 1
        # Convert tiles to cells
        self.send_event(('load_room', map_name, map_data))

    def _spawn_object_(self, object_type, x, y):
        identifier = str(uuid.uuid4())
        self.send_event(('spawn_object', object_type, identifier, x, y))
        if object_type in DOORS:
            object_class = 'door'
        else:
            object_class = 'item'
        self._game_objects_[identifier] = TrackedGameObject(identifier, object_class, object_type)
        self._game_objects_[identifier].position = (x, y)

    def _spawn_decoration_(self, decoration_type, x, y):
        self.send_event(('spawn_decoration', decoration_type, x, y))

    def _kill_object_(self, identifier):
        self.send_event(('kill_object', identifier))
        del self._game_objects_[identifier]

    def _open_door_(self, identifier):
        self.send_event(('open_door', identifier))

    def _get_objects_(self, type_id, exclude=None):
        found = []
        if exclude:
            if isinstance(exclude, TrackedGameObject):
                exclude = exclude.identifier
        for game_object in self._game_objects_.values():
            if game_object.identifier == exclude:
                continue
            if game_object.object_type == type_id:
                found.append(game_object)
        return found

    def _set_attribute_(self, identifier, attribute, value):
        self._game_objects_[identifier].attribute[attribute] = value
        self.send_event(('set_attribute', identifier, attribute, value))

    def _increase_attribute_(self, identifier, attribute, count):
        current_value = self._game_objects_[identifier].attribute.get(attribute, 0)
        self._game_objects_[identifier].attribute[attribute] = current_value + count
        self.send_event(('increase_attribute', identifier, attribute, count))

    def _spawn_player_(self):
        self.send_event(('spawn_player',))
        attributes = {
            TAGS: ['hero']
        }.update(self.parent_level.player.attribute)
        self._game_objects_[self.identifier] = TrackedGameObject(
            self.identifier, 'hero', 'player', attributes
        )

    def _warp_to_(self, identifier, position):
        self.send_event(('warp_to', identifier, position))
        self._game_objects_[identifier].position = position

    def _object_state_(self, identifier, state):
        self.send_event(('set_state', identifier, state))
        self._game_objects_[identifier].state = state

    def event_handler(self, event):
        '''Handle event from the Room()'''
        print('Processing: {}'.format(event))
        event_type = event[0]
        event_parameters = event[1:]

        if event_type == 'collision':
            self._process_collision_(*event_parameters)
        elif event_type == 'kill_object':
            if event_parameters[0] in self._game_objects_:
                del self._game_objects_[event_parameters[0]]

    def send_event(self, event):
        '''Send event to the Room()'''
        print('Sending: {}'.format(event))
        self._event_target_(event)

    def _process_collision_(self, object1, object2):
        if (object1 not in self._game_objects_) or (object2 not in self._game_objects_):
            return
        object1 = self._game_objects_[object1]
        object2 = self._game_objects_[object2]
        if object1.object_class == 'hero':
            if object2.object_class == 'item':
                # Player get an item
                if object2.object_type == game.objects.KEY:
                    self._kill_object_(object2.identifier)
                    self._increase_attribute_(object1.identifier, KEYS, 1)
                    self._increase_attribute_(object1.identifier, SCORE, POINTS_PER_KEY)
                elif object2.object_type == game.objects.TREASURE:
                    self._kill_object_(object2.identifier)
                    self._spawn_decoration_('smoke', *object2.position)
                    self._increase_attribute_(
                        object1.identifier, SCORE, random.randint(1, 4) * 1000
                    )
                elif object2.object_type == game.objects.JAR:
                    self._kill_object_(object2.identifier)
                    self._spawn_decoration_('smoke', *object2.position)
                    self._increase_attribute_(object1.identifier, LIFE, 100)
                elif object2.object_type == game.objects.HAM:
                    self._kill_object_(object2.identifier)
                    self._spawn_decoration_('smoke', *object2.position)
                    self._increase_attribute_(object1.identifier, LIFE, 50)
                elif object2.object_type == game.objects.TELEPORT:
                    destination = _closest_(
                        object1, self._get_objects_(game.objects.TELEPORT, exclude=object2)
                    )
                    if destination:
                        destination = _random_arround_(destination.position)
                        self._spawn_decoration_('smoke', *object1.position)
                        self._warp_to_(object1.identifier, destination)
                        self._spawn_decoration_('explosion', *destination)
                elif (object2.object_type == game.objects.EXIT) and (object1.state != 'exit'):
                    self._warp_to_(object1.identifier, object2.position)
                    self._object_state_(object1.identifier, 'exit')
                    self._increase_attribute_(object1.identifier, SCORE, POINTS_PER_LEVEL)
            elif object2.object_class == 'door':
                # Player try to open a door
                if object1.attribute.get(KEYS, 0) > 0:
                    self._increase_attribute_(object1.identifier, KEYS, -1)
                    self._increase_attribute_(object1.identifier, SCORE, POINTS_PER_DOOR)
                    self._open_door_(object2.identifier)

    def update(self):
        '''Game loop iteration'''
        if int(time.time()) != self._last_time_:
            for game_object in self._game_objects_.values():
                if game_object.object_class == 'hero':
                    self._increase_attribute_(game_object.identifier, LIFE, -1)
            self._last_time_ = int(time.time())
