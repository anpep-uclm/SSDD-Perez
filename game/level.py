#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
    Gauntlet engine
'''

import pyxel

import game
import game.room
import game.assets
import game.common
import game.heroes
import game.steers
import game.sprite
import game.pyxeltools

from game.common import LIFE, LEVELS, LEVEL_COUNT,\
    STATUS_SCREEN, GAME_OVER_SCREEN, GOOD_END_SCREEN


_KEY_ = game.sprite.Raster(game.pyxeltools.MAP_ENTITIES, *game.pyxeltools.tile(game.common.OSD_KEY))


def _discard_event_(event):
    print('Event ignored: {}'.format(event))


class NoLevel:
    '''Dummy object used when no level is loaded'''
    game_objects = {}
    def update(self):
        '''Do nothing'''
        pass

    def render(self):
        '''Draw nothing'''
        pass

    def spawn(self, actor):
        '''Spawn nothing'''
        pass


class Level(game.GameState):
    '''Level controller'''
    def __init__(self, parent):
        super(Level, self).__init__(parent)
        self._event_handler_ = _discard_event_
        self.room = NoLevel()
        self._orchestrator_ = None

    @property
    def player(self):
        '''Points to player data'''
        return self.parent.player

    @property
    def dungeon(self):
        '''Points to dungeon data'''
        return self.parent.dungeon

    @property
    def identifier(self):
        '''Unique game identifier'''
        return self.parent.identifier

    @property
    def orchestrator(self):
        '''Level orchestrator'''
        return self._orchestrator_

    @orchestrator.setter
    def orchestrator(self, new_orchestrator):
        '''Set the level orchestrator'''
        self._orchestrator_ = new_orchestrator
        self._event_handler_ = self._orchestrator_.event_handler
        self._orchestrator_.event_target = self.event_consumer
        self._orchestrator_.identifier = self.identifier
        self._orchestrator_.parent_level = self

    def wake_up(self):
        game.pyxeltools.load_png_to_image_bank(
            game.assets.search('map_entities.png'), game.pyxeltools.MAP_ENTITIES
        )
        game.pyxeltools.load_png_to_image_bank(
            game.assets.search('enemies.png'), game.pyxeltools.ENEMIES
        )
        game.pyxeltools.load_png_to_image_bank(
            game.assets.search('heroes.png'), game.pyxeltools.HEROES
        )
        self._orchestrator_.start()

    def suspend(self):
        self.room = NoLevel()

    def set_event_handler(self, event_handler):
        '''Change event hanlder'''
        self._event_handler_ = event_handler

    def update(self):
        self.orchestrator.update()
        self.room.update()

    def render(self):
        self.room.render()
        # OSD
        for k in range(self.room.game_objects[self.identifier].attribute.get(game.common.KEYS, 0)):
            _KEY_.render(4, 16 + (k * 10))
        pyxel.text(
            4, 4,
            f"LIFE: {self.room.game_objects[self.identifier].attribute.get(game.common.LIFE, 0)}",
            10
        )
        pyxel.text(
            4, 12,
            f"SCORE: {self.room.game_objects[self.identifier].attribute.get(game.common.SCORE, 0)}",
            10
        )

    def make_room(self, name, data):
        '''Room factory'''
        self.room = game.room.Room(data, self)

    def end_current_room(self):
        '''End level'''
        if self.player.attribute[LIFE] <= 0:
            self.go_to_state(GAME_OVER_SCREEN)
        else:
            if self.dungeon.finished:
                self.go_to_state(GOOD_END_SCREEN)
            else:
                self.player.attribute[LEVEL_COUNT] += 1
                self.go_to_state(STATUS_SCREEN)

    def spawn_player(self):
        '''Create a new player for this level'''
        hero = game.heroes.new(
            self.player.hero_class,
            actor_identifier=self.identifier, attributes=self.player.attribute
        )
        hero.steer = game.steers.new(self.player.steer_id)
        self.room.spawn(hero)
        self.room.camera.set_target(hero)
        self.room.camera.warp_to(hero.position)
        self.room.spawn_decoration('explosion', hero.position)

    def spawn_object(self, object_type, identifier, x, y):
        '''Create a new object'''
        self.room.spawn_at(game.objects.new(object_type, identifier), (x, y))

    def spawn_decoration(self, decoration_type, x, y):
        '''Create a new decoration'''
        self.room.spawn_decoration(decoration_type, (x, y))

    def warp_to(self, identifier, destination):
        '''Change object position by the given position'''
        source = self.room.game_objects.get(identifier, None)
        if not source:
            return
        source.position = destination

    def kill_object(self, identifier):
        '''Remove object from level'''
        self.room.kill(identifier)

    def open_door(self, door_identifier):
        '''Remove door (and adyacents)'''
        self.room.open_door(door_identifier)

    def set_game_object_attribute(self, identifier, attribute, value):
        '''Change attribute of a game object'''
        game_object = self.room.game_objects.get(identifier, None)
        if not game_object:
            return
        game_object.set_attribute(attribute, value)

    def increase_game_object_attribute(self, identifier, attribute, count):
        '''Increase/decrease attribute of a game object'''
        game_object = self.room.game_objects.get(identifier, None)
        if not game_object:
            return
        current_value = game_object.get_attribute(attribute, 0)
        game_object.set_attribute(attribute, current_value + count)

    def set_actor_direction(self, identifier, dir_x, dir_y):
        '''Change direction of an actor'''
        game_object = self.room.game_objects.get(identifier, None)
        if not game_object:
            return
        game_object.set_attribute(game.common.DIR_X, dir_x)
        game_object.set_attribute(game.common.DIR_Y, dir_y)

    def set_state(self, identifier, state):
        '''Change state of an object'''
        game_object = self.room.game_objects.get(identifier, None)
        if not game_object:
            return
        game_object.state = state

    def send_event(self, event):
        '''Send event to orchestrator'''
        self._event_handler_(event)

    def event_consumer(self, event):
        '''Consume event from orchestrator'''
        event_type = event[0]
        event_parameters = event[1:]
        if event_type == 'load_room':
            self.make_room(*event_parameters)
        elif event_type == 'spawn_player':
            self.spawn_player(*event_parameters)
        elif event_type == 'spawn_object':
            self.spawn_object(*event_parameters)
        elif event_type == 'spawn_decoration':
            self.spawn_decoration(*event_parameters)
        elif event_type == 'warp_to':
            self.warp_to(*event_parameters)
        elif event_type == 'kill_object':
            self.kill_object(*event_parameters)
        elif event_type == 'open_door':
            self.open_door(*event_parameters)
        elif event_type == 'set_attribute':
            self.set_game_object_attribute(*event_parameters)
        elif event_type == 'set_direction':
            self.set_actor_direction(*event_parameters)
        elif event_type == 'increase_attribute':
            self.increase_game_object_attribute(*event_parameters)
        elif event_type == 'set_state':
            self.set_state(*event_parameters)
