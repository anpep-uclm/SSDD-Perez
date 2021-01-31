#!/usr/bin/env python3
# coding: utf8
"""
game_server: Provides an interface for the game to obtain random maps
"""

import os
import sys
import argparse
import logging
import glob
import random
import Ice

Ice.loadSlice(
    f"{os.path.dirname(os.path.realpath(__file__))}/../icegauntlet.ice"
)
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet


class RoomManagerI(IceGauntlet.RoomManager):
    # pylint: disable=R0903

    """
    Game servant
    """

    def __init__(self):
        """
        Initializes this servant interface
        """
        self._create_data_directory()

    def _create_data_directory(self):
        """
        Creates a permanent data directory for storing maps
        """
        if os.path.isdir(self._get_data_dir()):
            logging.info("data directory OK")
            return
        os.makedirs(self._get_data_dir())

    @staticmethod
    def _get_data_dir() -> str:
        """
        Obtains the permanent data directory path
        :return The absolute path to the data directory
        """
        return os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "..", "data"
            )
        )

    # pylint: disable=C0103
    # pylint: disable=W0613
    def getRoom(self, current=None) -> str:
        """
        Obtains the data for a random room uploaded to the server
        :return The JSON string representing the room
        """
        matching_paths = glob.glob(
            os.path.join(self._get_data_dir(), "room_*.json")
        )
        if not matching_paths:
            logging.warning("no rooms were found in the data directory")
            raise IceGauntlet.RoomNotExists()

        with open(random.choice(matching_paths), "r") as room_file:
            return room_file.read()


class Server(Ice.Application):
    """
    Game server
    """

    def run(self, args: list) -> int:
        """
        Server loop
        :params args An argument list passed by the communicator initialization
        :return An exit code to the operating system
        """
        servant = RoomManagerI()
        adapter = self.communicator().createObjectAdapter("RoomManagerAdapter")
        proxy = adapter.add(
            servant, self.communicator().stringToIdentity("default")
        )

        adapter.addDefaultServant(servant, "")
        adapter.activate()

        logging.debug("adapter ready (servant proxy: %s)", proxy)
        print(f'"{proxy}"', flush=True)

        logging.debug("entering server loop")
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        logging.debug("bye!")
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", action="store_true", help="displays debug traces"
    )
    parser.add_argument("--config", help="ZeroC Ice config file")
    arguments = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    if not arguments.v:
        # disable all logging from levels CRITICAL and below, effectively
        # disabling any kind of logging
        logging.disable(logging.CRITICAL)

    server = Server()
    sys.exit(server.main(sys.argv, configFile=arguments.config))
