#!/usr/bin/env python3
# coding: utf8
"""
map_server: Executes the map management servant
"""

import os
import sys
import argparse
import logging
import hashlib
import base64
import json
import Ice

Ice.loadSlice(
    f"{os.path.dirname(os.path.realpath(__file__))}/../icegauntlet.ice"
)
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet


class MapManagementI(IceGauntlet.MapManagement):
    """
    Map management servant
    """

    def __init__(self, auth: IceGauntlet.AuthenticationPrx):
        """
        Initializes this servant interface
        :param auth An instance of an authentication server proxy
        """
        self._auth = auth
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
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "data")
        )

    @staticmethod
    def _get_room_file(room_name: str) -> str:
        """
        Obtains the path of the file associated to a room
        :param room_name Name of the room
        :return The absolute path to the room file path
        """
        room_id = hashlib.sha256(room_name.encode("utf8")).digest()
        encoded_room_id = base64.urlsafe_b64encode(room_id).decode("utf8")
        return os.path.join(
            MapManagementI._get_data_dir(), f"room_{encoded_room_id}.json"
        )

    # pylint: disable=W0613
    def publish(self, token: str, room_data: str, current=None):
        """
        Publishes a room. The client sends a room to the server and verifies
        the token against the authentication server.
        :param token Authentication token
        :param room_data JSON string representing the room
        """
        if not self._auth.isValid(token):
            logging.warning("invalid token: %s", token)
            raise IceGauntlet.Unauthorized()

        room_actual_data = json.loads(room_data)
        if set(room_actual_data.keys()) != set(("data", "room")):
            logging.warning("invalid format for room")
            raise IceGauntlet.InvalidRoomFormat()

        room_name = room_actual_data["room"]
        if not isinstance(room_name, str):
            logging.warning("no room name present on room data")
            raise IceGauntlet.InvalidRoomFormat()

        room_file_path = self._get_room_file(room_name)
        if os.path.isfile(room_file_path):
            logging.warning("room %s already exists", room_name)
            raise IceGauntlet.RoomAlreadyExists()

        logging.info("registering room %s", room_name)
        with open(room_file_path, "w") as room_file:
            room_file.write(room_data)

    # pylint: disable=W0613
    def remove(self, token: str, room_name: str, current=None):
        """
        Removes a room from the server
        :param token Authentication token
        :param room_name Name of the room to be removed
        """
        if not self._auth.isValid(token):
            logging.warning("invalid token: %s", token)
            raise IceGauntlet.Unauthorized()

        room_file_path = self._get_room_file(room_name)
        if not os.path.isfile(room_file_path):
            logging.warning("room %s does not exist", room_name)
            raise IceGauntlet.RoomNotExists()

        logging.info("deleting room %s", room_name)
        os.unlink(room_file_path)


class Server(Ice.Application):
    """
    Map management server
    """

    def run(self, args: list) -> int:
        """
        Server loop
        :params args An argument list passed by the communicator initialization
        :return An exit code to the operating system
        """
        # the first argument is always the authenticator proxy string
        auth_proxy = self.communicator().stringToProxy(args[0])

        logging.debug("resolving auth proxy: %s", auth_proxy)
        auth = IceGauntlet.AuthenticationPrx.checkedCast(auth_proxy)
        if not auth:
            raise RuntimeError("invalid authentication proxy")

        logging.info("auth proxy OK")
        servant = MapManagementI(auth)
        adapter = self.communicator().createObjectAdapter(
            "MapManagementAdapter"
        )
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
    parser.add_argument("auth_proxy", help="authentication proxy string")
    parser.add_argument("--config", help="ZeroC Ice config file")
    arguments = parser.parse_args()

    if arguments.v:
        # configure logging so it writes to stdout
        logging.basicConfig(level=logging.DEBUG)

    server = Server()
    sys.exit(server.main([arguments.auth_proxy], configFile=arguments.config))
