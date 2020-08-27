#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

''' Heroes factory '''

from game.common import WARRIOR, VALKYRIE, WIZARD, ELF,\
    HEROES_SPAWN, SPAWN_IDS, KEYS, HERO_CLASS, SCORE, LIFE,\
    INITIAL_HERO_LIFE
from game.game_object import Actor
from game.bodies import Box
from game.sprite import loop_animation, animation
from game.artwork import WARRIOR_UP, WARRIOR_DOWN, WARRIOR_LEFT, WARRIOR_RIGHT, WARRIOR_UP_LEFT,\
    WARRIOR_DOWN_LEFT, WARRIOR_UP_RIGHT, WARRIOR_DOWN_RIGHT, WARRIOR_EXIT,\
    VALKYRIE_UP, VALKYRIE_DOWN, VALKYRIE_LEFT, VALKYRIE_RIGHT, VALKYRIE_UP_LEFT,\
    VALKYRIE_DOWN_LEFT, VALKYRIE_UP_RIGHT, VALKYRIE_DOWN_RIGHT, VALKYRIE_EXIT,\
    WIZARD_UP, WIZARD_DOWN, WIZARD_LEFT, WIZARD_RIGHT, WIZARD_UP_LEFT, WIZARD_DOWN_LEFT,\
    WIZARD_UP_RIGHT, WIZARD_DOWN_RIGHT, WIZARD_EXIT,\
    ELF_UP, ELF_DOWN, ELF_LEFT, ELF_RIGHT, ELF_UP_LEFT, ELF_DOWN_LEFT, ELF_UP_RIGHT,\
    ELF_DOWN_RIGHT, ELF_EXIT
from game.pyxeltools import HEROES


class Hero(Actor):
    '''A hero actor (player)'''
    def __init__(self, animations, identifier, spawn_zone):
        super(Hero, self).__init__(animations, identifier=identifier)
        self._spawn_ = spawn_zone
        self.body = Box()
        self.tags.append('hero')
        self.set_attribute(KEYS, 0)

    @property
    def spawn(self):
        '''Spawn area to use'''
        return self._spawn_

    @spawn.setter
    def spawn(self, new_spawn):
        '''Set spawn area to use'''
        if new_spawn not in SPAWN_IDS:
            raise ValueError('Invalid spawn_id "{}"'.format(new_spawn))
        self._spawn_ = new_spawn


def new(hero_type, actor_identifier=None, attributes=None):
    '''Hero factory'''
    attributes = attributes or {}
    if hero_type == WARRIOR:
        new_actor = Hero({
            'stand_by': loop_animation(HEROES, 4, [WARRIOR_DOWN[0]]),
            'up': loop_animation(HEROES, 4, WARRIOR_UP),
            'up_right': loop_animation(HEROES, 4, WARRIOR_UP_RIGHT),
            'right': loop_animation(HEROES, 4, WARRIOR_RIGHT),
            'down_right': loop_animation(HEROES, 4, WARRIOR_DOWN_RIGHT),
            'down': loop_animation(HEROES, 4, WARRIOR_DOWN),
            'down_left': loop_animation(HEROES, 4, WARRIOR_DOWN_LEFT),
            'left': loop_animation(HEROES, 4, WARRIOR_LEFT),
            'up_left': loop_animation(HEROES, 4, WARRIOR_UP_LEFT),
            'exit': animation(HEROES, 4, WARRIOR_EXIT)
        }, identifier=actor_identifier, spawn_zone=HEROES_SPAWN[hero_type])

    elif hero_type == VALKYRIE:
        new_actor = Hero({
            'stand_by': loop_animation(HEROES, 3, [VALKYRIE_DOWN[0]]),
            'up': loop_animation(HEROES, 3, VALKYRIE_UP),
            'up_right': loop_animation(HEROES, 3, VALKYRIE_UP_RIGHT),
            'right': loop_animation(HEROES, 3, VALKYRIE_RIGHT),
            'down_right': loop_animation(HEROES, 3, VALKYRIE_DOWN_RIGHT),
            'down': loop_animation(HEROES, 3, VALKYRIE_DOWN),
            'down_left': loop_animation(HEROES, 3, VALKYRIE_DOWN_LEFT),
            'left': loop_animation(HEROES, 3, VALKYRIE_LEFT),
            'up_left': loop_animation(HEROES, 3, VALKYRIE_UP_LEFT),
            'exit': animation(HEROES, 4, VALKYRIE_EXIT)
        }, identifier=actor_identifier, spawn_zone=HEROES_SPAWN[hero_type])

    elif hero_type == WIZARD:
        new_actor = Hero({
            'stand_by': loop_animation(HEROES, 4, [WIZARD_DOWN[0]]),
            'up': loop_animation(HEROES, 4, WIZARD_UP),
            'up_right': loop_animation(HEROES, 4, WIZARD_UP_RIGHT),
            'right': loop_animation(HEROES, 4, WIZARD_RIGHT),
            'down_right': loop_animation(HEROES, 4, WIZARD_DOWN_RIGHT),
            'down': loop_animation(HEROES, 4, WIZARD_DOWN),
            'down_left': loop_animation(HEROES, 4, WIZARD_DOWN_LEFT),
            'left': loop_animation(HEROES, 4, WIZARD_LEFT),
            'up_left': loop_animation(HEROES, 4, WIZARD_UP_LEFT),
            'exit': animation(HEROES, 4, WIZARD_EXIT)
        }, identifier=actor_identifier, spawn_zone=HEROES_SPAWN[hero_type])

    elif hero_type == ELF:
        new_actor = Hero({
            'stand_by': loop_animation(HEROES, 2, [ELF_DOWN[0]]),
            'up': loop_animation(HEROES, 2, ELF_UP),
            'up_right': loop_animation(HEROES, 2, ELF_UP_RIGHT),
            'right': loop_animation(HEROES, 2, ELF_RIGHT),
            'down_right': loop_animation(HEROES, 2, ELF_DOWN_RIGHT),
            'down': loop_animation(HEROES, 2, ELF_DOWN),
            'down_left': loop_animation(HEROES, 2, ELF_DOWN_LEFT),
            'left': loop_animation(HEROES, 2, ELF_LEFT),
            'up_left': loop_animation(HEROES, 2, ELF_UP_LEFT),
            'exit': animation(HEROES, 3, ELF_EXIT)
        }, identifier=actor_identifier, spawn_zone=HEROES_SPAWN[hero_type])

    else:
        raise ValueError('Invalid hero_type: {}'.format(hero_type))

    new_actor.attribute[HERO_CLASS] = hero_type
    new_actor.attribute[SCORE] = 0
    new_actor.attribute[LIFE] = INITIAL_HERO_LIFE
    new_actor.attribute.update(attributes)
    return new_actor
