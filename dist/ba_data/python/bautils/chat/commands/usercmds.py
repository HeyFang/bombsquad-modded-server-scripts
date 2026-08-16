# Released under the MIT License. See LICENSE for details.
#
"""A command module handing user commands."""

from typing import override

import bascenev1 as bs
from bautils.chat import (
    ServerCommand,
    register_command,
    NoArgumentsProvidedError,
    IncorrectUsageError,
)

# Removed unused Color import


@register_command
class List(ServerCommand):
    """/l, /list or /clients"""

    aliases = ["l", "clients"]

    @override
    def on_command_call(self) -> None:

        # Build and broadcast a clean ASCII player list table.
        header = "{0:^9} | {1:<16} | {2:^6}"
        separator = "-" * 40

        lines = []
        lines.append(separator)
        lines.append(header.format("ClientID", "Name", "Ping"))
        lines.append(separator)

        session = bs.get_foreground_host_session()
        assert session is not None

        for player in session.sessionplayers:
            client_id = player.inputdevice.client_id

            # Get ping safely
            try:
                ping = bs.get_client_ping(client_id)
                ping = f"{int(ping)}ms" if ping is not None else "-"
            except Exception:
                ping = "-"

            lines.append(
                header.format(
                    client_id,
                    player.getname(icon=True),
                    ping,
                )
            )

        lines.append(separator)
        _list = "\n".join(lines)

        bs.broadcastmessage(
            _list,
            transient=True,
            clients=[self.client_id],
        )
    @override
    def admin_authentication(self) -> bool:
        return False


@register_command
class Info(ServerCommand):
    """/info <client_id> — show the target client's player profiles."""

    aliases: list[str] = ["gp", "profiles"]

    @override
    def on_command_call(self) -> None:
        # Follow project style: use self.arguments with match/case
        match self.arguments:
            case []:
                # No args provided
                raise NoArgumentsProvidedError(
                    "Please provide neccesary arguments."
                )

            case [client_id] if client_id.isdigit():
                _id = self.filter_client_id(client_id)
                target = self.get_session_player(_id)

                try:
                    acc_id = target.get_account_id()
                    short_name = target.inputdevice.get_v1_account_name(
                        full=False
                    )
                except Exception:
                    acc_id = "N/A"
                    short_name = "N/A"

                # Build display message with profiles on that input device.
                try:
                    profiles = target.inputdevice.get_player_profiles()

                except Exception:
                    profiles = {}  # Initialize as empty dict instead of list

                profile_names = [
                    p for p in profiles.keys() if p != "__account__"
                ][:10]
                header = f"{"Sr.no":<9} |    {"Name":<12}\n" + ("-" * 25) + "\n"
                line0 = f"{acc_id} | {short_name}" + "\n"
                lines = [header, line0]
                for i, profile in enumerate(profile_names, start=1):
                    try:
                        lines.append(f"{i:<9} {profile:<12}\n")
                    except Exception:
                        # Skip any odd encodings gracefully
                        continue

                message = (
                    "".join(lines) if len(lines) > 1 else "No profiles found."
                )
                bs.broadcastmessage(
                    message, transient=True, clients=[self.client_id]
                )

            case _:
                # Wrong usage/signature
                raise IncorrectUsageError

    @override
    def admin_authentication(self) -> bool:
        # Let anyone use /info
        return False


@register_command
class hello(ServerCommand):
    """/hello - A simple test command."""

    @override
    def on_command_call(self) -> None:
        # session = bs.get_foreground_host_session()
        # if not session:
        #     return

        # for player in session.sessionplayers:
        #     client_id = player.inputdevice.client_id
        #     if (
        #         client_id is not None and client_id != -1
        #     ):  # Check for valid client ID
        #         try:
        #             ip = bs.get_client_ip_address(client_id=client_id)
        #             if ip:
        #                 print(
        #                     f"Player '{player.getname()}' (Client ID: {client_id}) IP: {ip}"
        #                 )
        #             else:
        #                 print(
        #                     f"Player '{player.getname()}' (Client ID: {client_id}) IP: Not available"
        #                 )
        #         except Exception as e:
        #             print(f"Error getting IP for Client ID {client_id}: {e}")
        #     else:
        #         print(f"Player '{player.getname()}' is not a remote client.")
        bs.broadcastmessage(
            f"Hello, {self.get_session_player(self.client_id).getname()}!",
            transient=True,
            clients=[self.client_id],
        )

    @override
    def admin_authentication(self) -> bool:
        return False
