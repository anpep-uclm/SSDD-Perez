#!/usr/bin/env python3
# coding: utf8
"""
map_client: Communicates with a map server to perform operations on maps
"""


import os
import sys
import argparse
import logging

import Ice

Ice.loadSlice(
    f"{os.path.dirname(os.path.realpath(__file__))}/../icegauntlet.ice"
)
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet


class Client(Ice.Application):
    """
    Map client
    """

    def run(self, args: list) -> int:
        """
        Client entry point
        :params args An argument list containing the communicator initialization parameters
        :return An exit code to the operating system
        """
        token, proxy, action, data = args
        if action not in ("publish", "remove"):
            raise RuntimeError(
                "invalid action (supported actions are publish and remove)"
            )

        maps_proxy = self.communicator().stringToProxy(proxy)

        logging.debug("resolving maps proxy: %s", maps_proxy)
        maps = IceGauntlet.MapManagementPrx.checkedCast(maps_proxy)
        if not maps:
            raise RuntimeError("invalid maps proxy")

        logging.info("maps proxy OK")

        try:
            if action == "publish":
                with open(data, "r") as room_file:
                    maps.publish(token, room_file.read())
            elif action == "remove":
                maps.remove(token, data)
        except IceGauntlet.Unauthorized:
            print("error: unauthorized", file=sys.stderr)
            return 1
        except IceGauntlet.RoomAlreadyExists:
            print("error: room already exists", file=sys.stderr)
            return 1
        except IceGauntlet.RoomNotExists:
            print("error: no such room", file=sys.stderr)
            return 1

        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", action="store_true", help="displays debug traces"
    )
    parser.add_argument("-t", help="authentication token")
    parser.add_argument("-p", help="maps proxy string")

    parser.add_argument(
        "action",
        metavar="publish|remove",
        help="action to perform (publish, remove)",
    )
    parser.add_argument(
        "data",
        metavar="room_name|room_data",
        help="data associated with the action",
    )

    arguments = parser.parse_args()

    if arguments.v:
        # configure logging so it writes to stdout
        logging.basicConfig(level=logging.DEBUG)

    client = Client()
    sys.exit(
        client.main(
            [arguments.t, arguments.p, arguments.action, arguments.data]
        )
    )
