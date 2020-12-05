#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
    Handling room events and objects
'''

import logging

from game.layer import TileMapLayer
from game.camera import Camera
from game.common import TILE_ID, DEFAULT_SPAWN
from game.objects import Spawn, Door
from game.pyxeltools import get_color_mask
from game.artwork import BLOCK_CELLS
import game.decoration


_DOOR_DIRECTION_ = {
    19: [(0, -1)],
    20: [(1, 0)],
    21: [(0, -1), (1, 0)],
    22: [(0, 1)],
    23: [(0, -1), (0, 1)],
    24: [(1, 0), (0, 1)],
    25: [(0, -1), (1, 0), (0, 1)],
    26: [(-1, 0)],
    27: [(-1, 0), (0, -1)],
    28: [(-1, 0), (1, 0)],
    29: [(0, -1), (-1, 0), (1, 0)],
    30: [(-1, 0), (0, 1)],
    31: [(0, -1), (-1, 0), (0, 1)],
    32: [(-1, 0), (0, 1), (1, 0)],
    33: [(0, -1), (-1, 0), (0, 1), (1, 0)]
}


class Room:
    '''Container for all in-game elements'''
    def __init__(self, floor_data, parent_game):
        self._scenario_ = TileMapLayer(floor_data, mask=get_color_mask())
        self._camera_ = Camera(self._scenario_)
        self._game_ = parent_game
        self._game_objects_ = {}
        self._decorations_ = {}
        self.block = self._compute_walls_collisions_()
        self._spawns_ = self._get_spawns_()

    @property
    def initial_objects(self):
        '''List of all objects defined in the map initially'''
        return self._scenario_.objects

    @property
    def game_objects(self):
        '''Map of current-living objects'''
        return self._game_objects_

    def _compute_walls_collisions_(self):
        block = []
        for y in range(self._scenario_.map_height):
            row = []
            for x in range(self._scenario_.map_width):
                row.append(self._scenario_.get_cell_at(x, y) in BLOCK_CELLS)
            block.append(row)
        return block

    def _get_spawns_(self):
        spawns = {}
        for candidate in self._game_objects_.values():
            if isinstance(candidate, Spawn):
                spawns[candidate.spawn] = candidate.position
        return spawns

    @property
    def camera(self):
        '''Room camera'''
        return self._camera_

    def set_camera_target(self, game_object):
        '''Change target of the camera'''
        self._camera_.set_target(game_object)

    @property
    def tilemaps(self):
        '''Map layers'''
        return self._scenario_

    def spawn(self, game_object):
        '''Spawn new object at a spawn zone'''
        spawn_zone = game_object.spawn if game_object.spawn in self._spawns_ else DEFAULT_SPAWN
        self.spawn_at(game_object, self._spawns_[spawn_zone])

    def spawn_at(self, game_object, position):
        '''Spawn new object at a given position'''
        self._game_objects_[game_object.identifier] = game_object
        self._game_objects_[game_object.identifier].position = position
        self._game_objects_[game_object.identifier].room = self
        self._spawns_.update(self._get_spawns_())

    def spawn_decoration(self, decoration_id, position):
        '''Spawn decoration'''
        decoration = game.decoration.new(decoration_id, position)
        self._decorations_[decoration.identifier] = decoration
        self._decorations_[decoration.identifier].room = self

    def kill(self, game_object):
        '''Kill an object'''
        identifier = game_object if isinstance(game_object, str) else game_object.identifier

        if identifier == self._game_.identifier:
            self._game_.player.attribute.update(self._game_objects_[identifier].attribute)

        if identifier in self._game_objects_:
            self._game_objects_[identifier].room = None
            del self._game_objects_[identifier]
        elif identifier in self._decorations_:
            self._decorations_[identifier].room = None
            del self._decorations_[identifier]

        if identifier == self._game_.identifier:
            self._game_.end_current_room()

    def open_door(self, door_identifier):
        '''Open a existing door'''
        door_position = self._search_door_(door_identifier)
        if not door_position:
            return
        doors = self._adjacent_doors_(door_position)
        for door in doors:
            self.kill(door)
            self.send_event(('kill_object', door))

    def _search_door_(self, door_identifier):
        if door_identifier not in self._game_objects_:
            return None
        y = 0
        for row in self.block:
            x = 0
            for cell in row:
                if cell == door_identifier:
                    return (x, y)
                x += 1
            y += 1
        return None

    def _adjacent_doors_(self, location, visited=None):
        if not visited:
            visited = []
        x, y = location
        if location in visited:
            return []
        visited.append((x, y))
        if (y not in range(len(self.block))) or (x not in range(len(self.block[0]))):
            return []
        identifier = self.block[y][x]
        try:
            door = self._game_objects_[identifier]
        except KeyError:
            logging.debug('Malformed map, object not found: {}'.format(identifier))
            return []
        if not isinstance(door, Door):
            return []
        doors = [door.identifier]
        door_tile_id = door.attribute[TILE_ID]
        for dir_x, dir_y in _DOOR_DIRECTION_[door_tile_id]:
            doors += self._adjacent_doors_((x + dir_x, y + dir_y), visited)
        return doors

    def update(self):
        '''A game loop iteration'''
        for game_object in list(self._game_objects_.values()):
            game_object.update()
            if not game_object.acting:
                self.kill(game_object)
            if game_object.body:
                self.check_collisions_with(game_object)

    def render(self):
        '''Draw a frame'''
        self._camera_.update()
        self._scenario_.render(*self._camera_.position)

        for game_object in self._game_objects_.values():
            game_object.render(*self._camera_.position)

        for decoration in list(self._decorations_.values()):
            decoration.render(*self._camera_.position)

    def check_collisions_with(self, game_object):
        '''Compute collisions for all game objects'''
        if not game_object.body:
            return
        for other_game_object in list(self._game_objects_.values()):
            if (other_game_object is game_object) or (not other_game_object.body):
                continue
            if game_object.body.collides_with(other_game_object):
                self.send_event(('collision', game_object.identifier, other_game_object.identifier))

    def send_event(self, event):
        '''Send event to orchestrator'''
        self._game_.send_event(event)
