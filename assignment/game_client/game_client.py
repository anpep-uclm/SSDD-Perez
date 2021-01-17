#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=W1203

"""
    ICE Gauntlet LOCAL GAME
"""

import os
import sys
import logging
import argparse
import Ice

Ice.loadSlice(
    f"{os.path.dirname(os.path.realpath(__file__))}/../icegauntlet.ice"
)
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

# add the top level directory to the module search path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..")
    )
)

import game
import game.common
import game.screens
import game.pyxeltools
import game.orchestration

DEFAULT_HERO = game.common.HEROES[0]


class RemoteDungeonMap:
    """
    Procedurally obtains levels from the remote server
    """

    def __init__(self, game_proxy: IceGauntlet.GamePrx):
        """
        Initializes the remote dungeon map
        :param game_proxy An instance of the Game proxy
        """
        self._game_proxy = game_proxy

    @property
    def next_room(self) -> str:
        """
        Gets the next room data
        """
        return self._game_proxy.getRoom()

    @property
    def finished(self):
        """
        Returns whether or not the game is finished
        """
        # online games never seem to come to an end!
        return False


class Client(Ice.Application):
    """
    Game client
    """

    def run(self, args: list) -> int:
        """
        Client entry point
        :params args An argument list containing the communicator initialization parameters
        :return An exit code to the operating system
        """
        proxy, hero = args
        game_proxy = self.communicator().stringToProxy(proxy)

        logging.debug("resolving game proxy: %s", game_proxy)
        game_prx = IceGauntlet.GamePrx.checkedCast(game_proxy)
        if not game:
            raise RuntimeError("invalid game proxy")

        logging.info("game proxy OK")

        game.pyxeltools.initialize()
        dungeon = RemoteDungeonMap(game_prx)
        gauntlet = game.Game(hero, dungeon)
        gauntlet.add_state(game.screens.TileScreen, game.common.INITIAL_SCREEN)
        gauntlet.add_state(game.screens.StatsScreen, game.common.STATUS_SCREEN)
        gauntlet.add_state(game.screens.GameScreen, game.common.GAME_SCREEN)
        gauntlet.add_state(
            game.screens.GameOverScreen, game.common.GAME_OVER_SCREEN
        )
        gauntlet.add_state(
            game.screens.GoodEndScreen, game.common.GOOD_END_SCREEN
        )
        gauntlet.start()

        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("game_proxy", help="Proxy string for the game server")
    parser.add_argument(
        "-v", action="store_true", help="displays debug traces"
    )
    parser.add_argument(
        "-p",
        "--player",
        default=DEFAULT_HERO,
        choices=game.common.HEROES,
        dest="hero",
        help="Hero to play with",
    )

    arguments = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    if not arguments.v:
        # disable all logging from levels CRITICAL and below, effectively
        # disabling any kind of logging
        logging.disable(logging.CRITICAL)

    client = Client()
    sys.exit(client.main([arguments.game_proxy, arguments.hero]))
