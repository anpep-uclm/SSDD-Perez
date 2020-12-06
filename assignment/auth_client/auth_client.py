#!/usr/bin/env python3
# coding: utf8
"""
auth_client: Provides access to authentication server operations
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

PASSWORD_SALT = """
Our hard work by these
words guarded please don’t steal
(c)Apple Computer Inc
""".strip()


class Client(Ice.Application):
    """
    Authentication client
    """

    @staticmethod
    def _calculate_hash(password: str) -> str:
        """
        Calculates the hash for the provided password
        :param password Password for which the hash will be calculated for
        :return The hash calculated for this password
        """
        if password is None:
            return None
        password_hash = hashlib.sha256()
        password_hash.update(PASSWORD_SALT.encode("utf8"))
        password_hash.update(password.encode("utf8"))
        return password_hash.hexdigest()

    def run(self, args: list) -> int:
        """
        Client entry point
        :param args An argument list containing the communicator initialization parameters
        :return An exit code to the operating system
        """
        proxy, action, user = args
        auth_proxy = self.communicator().stringToProxy(proxy)

        logging.debug("resolving auth proxy: %s", auth_proxy)
        auth = IceGauntlet.AuthenticationPrx.checkedCast(auth_proxy)
        if not auth:
            raise RuntimeError("invalid authentication proxy")

        logging.info("auth proxy OK")

        if action == "reset":
            logging.debug("resetting password for user %s", user)
            old_password = getpass.getpass("old password: ")
            if len(old_password.strip()) == 0:
                logging.debug("no password provided")
                old_password = None
            new_password = getpass.getpass("new password: ")
            try:
                auth.changePassword(
                    user,
                    self._calculate_hash(old_password),
                    self._calculate_hash(new_password),
                )
            except IceGauntlet.Unauthorized:
                print("error: unauthorized", file=sys.stderr)
                return 1
        elif action == "token":
            logging.debug("obtaining token for user %s", user)
            password = getpass.getpass("password: ")
            try:
                print(auth.getNewToken(user, self._calculate_hash(password)))
            except IceGauntlet.Unauthorized:
                print("error: unauthorized", file=sys.stderr)
                return 1
        else:
            print("error: invalid action", file=sys.stderr)
            return 1

        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", action="store_true", help="displays debug traces"
    )
    parser.add_argument("-p", help="authenticator proxy string")
    parser.add_argument(
        "action",
        metavar="reset|token",
        help="action to perform (reset, token)",
    )
    parser.add_argument(
        "user",
        metavar="user",
        help="user name",
    )

    arguments = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    if not arguments.v:
        # disable all logging from levels CRITICAL and below, effectively
        # disabling any kind of logging
        logging.disable(logging.CRITICAL)

    client = Client()
    sys.exit(client.main([arguments.p, arguments.action, arguments.user]))
