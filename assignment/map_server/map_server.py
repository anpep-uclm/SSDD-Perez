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
import IceStorm

Ice.loadSlice(
    f"{os.path.dirname(os.path.realpath(__file__))}/../icegauntlet.ice"
)
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

class RoomManagerSyncI(IceGauntlet.RoomManagerSync):
    def __init__(self):
        self._room_managers = {}
        pass

    def hello(self, room_manager, manager_id: str):
        logging.info('room manager %s registered', manager_id)
        self._room_managers[manager_id] = room_manager

    def announce(self, room_manager, manager_id: str):
        pass

    def newRoom(self, room_name: str, manager_id: str):
        pass

    def removedRoom(self, room_name, manager_id: str):
        pass

class RoomManagerI(IceGauntlet.RoomManager):
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
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "..", "data"
            )
        )

    @staticmethod
    def _get_room_file(user_name: str, room_name: str) -> str:
        """
        Obtains the path of the file associated to a room
        :param user_name Name of the owner
        :param room_name Name of the room
        :return The absolute path to the room file path
        """
        room_id = hashlib.sha256(room_name.encode("utf8")).digest()
        user_id = hashlib.sha1(user_name.encode("utf8")).digest()
        encoded_room_id = base64.urlsafe_b64encode(room_id).decode("utf8")
        encoded_user_id = base64.urlsafe_b64encode(user_id).decode("utf8")
        return os.path.join(
            RoomManagerI._get_data_dir(), f"room_{encoded_user_id}_{encoded_room_id}.json"
        )

    # pylint: disable=W0613
    def publish(self, token: str, room_data: str, current=None):
        """
        Publishes a room. The client sends a room to the server and verifies
        the token against the authentication server.
        :param token Authentication token
        :param room_data JSON string representing the room
        """
        try:
            user_name = self._auth.getOwner(token)
        except IceGauntlet.Unauthorized:
            logging.warning("invalid token: %s", token)
            raise IceGauntlet.Unauthorized
        room_actual_data = json.loads(room_data)
        if set(room_actual_data.keys()) != {"data", "room"}:
            logging.warning("invalid format for room")
            raise IceGauntlet.WrongRoomFormat()

        room_name = room_actual_data["room"]
        if not isinstance(room_name, str):
            logging.warning("no room name present on room data")
            raise IceGauntlet.WrongRoomFormat()

        room_file_path = self._get_room_file(user_name, room_name)
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
        try:
            user_name = self._auth.getOwner(token)
        except IceGauntlet.Unauthorized:
            logging.warning("invalid token: %s", token)
            raise IceGauntlet.Unauthorized

        room_file_path = self._get_room_file(user_name, room_name)
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
        auth_proxy = self.communicator().stringToProxy(args[1])

        logging.debug("resolving auth proxy: %s", auth_proxy)
        auth = IceGauntlet.AuthenticationPrx.checkedCast(auth_proxy)
        if not auth:
            raise RuntimeError("invalid authentication proxy")

        logging.info("auth proxy OK")

        manager_servant, event_servant = RoomManagerI(auth), RoomManagerSyncI()
        manager_adapter = self.communicator().createObjectAdapter("RoomManagerAdapter")
        event_adapter = self.communicator().createObjectAdapter("RoomManagerSyncAdapter")
        identity = self.communicator().getProperties().getProperty('Identity')

        manager_proxy = manager_adapter.add(manager_servant, self.communicator().stringToIdentity(identity))
        event_proxy = event_adapter.addWithUUID(event_servant)

        manager_adapter.addDefaultServant(manager_servant, "")
        manager_adapter.activate()

        event_adapter.addDefaultServant(event_servant, "")
        event_adapter.activate()

        logging.debug('manager servant: %s', manager_proxy)
        logging.debug('event servant: %s', event_proxy)

        logging.debug("entering server loop")
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        logging.debug("bye!")
        return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = Server()
    sys.exit(app.main(sys.argv))
