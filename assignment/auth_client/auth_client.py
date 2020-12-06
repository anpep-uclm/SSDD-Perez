#!/usr/bin/env python3
# coding: utf8
"""
auth_client: Authenticates against the provided server and obtains an auth token
"""


import os
import sys
import argparse
import logging
import getpass
import hashlib

import Ice

Ice.loadSlice(
    f"{os.path.dirname(os.path.realpath(__file__))}/../icegauntlet.ice"
)
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet


class Client(Ice.Application):
    """
    Authentication client
    """

    def run(self, args: list) -> int:
        """
        Client entry point
        :params args An argument list containing the communicator initialization parameters
        :return An exit code to the operating system
        """
        user, proxy = args
        auth_proxy = self.communicator().stringToProxy(proxy)

        logging.debug("resolving auth proxy: %s", auth_proxy)
        auth = IceGauntlet.AuthenticationPrx.checkedCast(auth_proxy)
        if not auth:
            raise RuntimeError("invalid authentication proxy")

        logging.info("auth proxy OK")

        password = getpass.getpass("password: ")
        logging.debug("authenticating user %s against server", user)

        try:
            print(
                auth.getNewToken(
                    user, hashlib.sha256(password.encode("utf8")).hexdigest()
                ),
                flush=True,
            )
        except IceGauntlet.Unauthorized:
            print("error: unauthorized", file=sys.stderr)
            return 1

        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", action="store_true", help="displays debug traces"
    )
    parser.add_argument("user", help="user name")
    parser.add_argument("auth_proxy", help="authentication proxy string")
    arguments = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    if not arguments.v:
        # disable all logging from levels CRITICAL and below, effectively
        # disabling any kind of logging
        logging.disable(logging.CRITICAL)

    client = Client()
    sys.exit(client.main([arguments.user, arguments.auth_proxy]))
