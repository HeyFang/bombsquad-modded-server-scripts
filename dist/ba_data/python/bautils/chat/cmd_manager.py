# Released under the MIT License. See LICENSE for details.
#
"""A chat interpreter to manage chat related things."""

from __future__ import annotations

from typing import TYPE_CHECKING
import bascenev1 as bs

# import settings
try:
    from .. import settings
except ImportError:
    print(
        "\nERROR: Could not import settings.py from bautils directory."
        " Discord admin auth will be disabled."
    )

    # Define a dummy module with default False if import fails
    class DummySettings:
        enablePasswordAuth = False
        enableIpAuth = False
        authorizedAdminIPs = []
        adminPassword = "watermelon"

    settings = DummySettings()


if TYPE_CHECKING:
    from .server_command import ServerCommand


class CommandManager:
    """Factory Managing server commands."""

    commands: dict[str, ServerCommand] = {}
    verified_admins: dict[int, str] = {}

    @classmethod
    def add_command(cls, command: ServerCommand) -> None:
        """
        Add a command to a command factory.

        Args:
            command (ServerCommand): Command class must inherit this
            class to execute.
        """
        # Get the class name if name is not provided
        if command.name is None:
            command.name = command.__class__.__name__
        cmd_key = command.command_prefix() + command.name.upper()
        cls.commands[cmd_key] = command
        for alias in command.aliases:
            alias_key = command.command_prefix() + alias.upper()
            cls.commands[alias_key] = command

    # verification-
    @classmethod
    def mark_admin_verified(cls, client_id: int, shortname: str) -> bool:
        """
        Verify an admin based on current client_id and shortname match.
        If successful, stores the client_id -> shortname mapping.
        Returns True on success, False otherwise.
        """
        try:
            session = bs.get_foreground_host_session()
            player = None
            if session:
                for p in session.sessionplayers:
                    if p.inputdevice.client_id == client_id:
                        player = p
                        break

            # Check if player exists AND their current shortname matches the one provided
            if player and player.getname(full=False, icon=False) == shortname:
                # Store the mapping
                cls.verified_admins[client_id] = shortname
                print(
                    f"Admin client_id {client_id} (Name: {shortname}) verified via external source."
                )
                bs.broadcastmessage(
                    "Admin verification successful.",
                    clients=[client_id],
                    transient=True,
                    color=(0, 1, 0),
                )
                return True  # Verification successful
            return False  # Verification failed

        except Exception as e:
            print(
                f"Error in mark_admin_verified for client_id {client_id}, name {shortname}: {e}"
            )
            return False  # Verification failed due to error

    # check verification
    @classmethod
    def is_admin_verified(cls, client_id: int, current_shortname: str) -> bool:
        """
        Checks if client_id is verified AND the stored name matches the current name.
        """
        verified_name = cls.verified_admins.get(client_id)
        # Return True only if client_id is found AND the stored name matches the current name
        if verified_name is not None and verified_name == current_shortname:
            return True
        return False

    # remove verification if needed (not used currently)
    @classmethod
    def remove_verified_admin(cls, client_id: int) -> None:
        """Remove a client_id from verification when they disconnect."""
        if client_id in cls.verified_admins:
            del cls.verified_admins[client_id]
            # Optional: print(f"Removed client_id {client_id} from verified admins.")

    @classmethod
    def listen(cls, msg: str, client_id: int) -> str | None:
        """
        A custom hook connecting commands to the game chat.

        Args:
            msg (str): message content
            client_id (int): special ID of a player

        Returns:
            str | None: Returns back original message, ignores if None.
        """

        # get the beggining of the of the message and get command.
        # capitalize it to match all cases.
        if not msg or not msg.strip():
            return None  # <- ignore empty messages completely

        if msg.startswith("/login"):
            parts = msg.split()

            # usage check
            if len(parts) < 2:
                print(f"LOGIN: {client_id}: wrong cmd {msg}")
                return None

            entered_pass = parts[1]

            actual_pass = getattr(settings, 'adminPassword', 'watermelon')

            #password check
            if entered_pass == actual_pass:
                #get player name for storage
                try:
                    session = bs.get_foreground_host_session()
                    player_name = "Unknown"
                    if session:
                        for p in session.sessionplayers:
                            if p.inputdevice.client_id == client_id:
                                player_name = p.getname(full=False, icon=False)
                                break

                    #Mark verified
                    cls.mark_admin_verified(client_id, player_name)

                except Exception as e:
                    print(f"Login error: {e}")

            else:
                bs.broadcastmessage(
                    "Incorrect Password",
                    clients=[client_id],
                    transient=True,
                    color=(1,0,0)
                )
                print(f"{client_id}: wrong pass- {msg}")

            #hide cmd from chat
            return None


        # standard cmds
        parts = msg.split()
        if not parts:
            return None

        cmd = parts[0]
        prefix = cmd[0]  # Keep original prefix case
        cmd_name = cmd[1:].upper()  # Convert only command name to upper

        command = cls.commands.get(prefix + cmd_name)

        if command is not None:
            # set some attributes for abtraction
            command.client_id = client_id
            command.message = msg
            # print(f"DEBUG: Command '{cmd}' received from client_id {client_id}.") # DEBUG 1

            if command.admin_authentication():
                # check admins from loaded config file.
                if command.is_admin:
                    # print(f"DEBUG: Client {client_id} IS an admin (pb-id check passed).") # DEBUG 2

                    # settings checks
                    # default to False if settings are missing
                    ip_auth_enabled = getattr(settings, 'enableIpAuth', False)
                    password_auth_enabled = getattr(settings,'enablePasswordAuth', False)
                    # print(f"DEBUG: Current verified_admins dict: {cls.verified_admins}")

                    # IP CHECK
                    if ip_auth_enabled:
                        # IP address check
                        try:
                            client_ip = bs.get_client_ip_address(
                                client_id=client_id
                            )
                            authorized_ips = getattr(
                                settings, 'authorizedAdminIPs', []
                            )
                            if client_ip not in authorized_ips:
                                print(
                                    f"Client {client_id} IP '{client_ip}' not in authorized admin IPs."
                                )
                                bs.broadcastmessage(
                                    "❌ Access Denied!",
                                    clients=[client_id],
                                    transient=True,
                                    color=(1, 0, 0),
                                )
                                return None  # Block command execution
                            else:
                                # print(f"Client {client_id} IP '{client_ip}' passed IP auth check.")
                                pass
                        except Exception as e:
                            print(
                                f"Error getting IP for client_id {client_id}: {e}"
                            )
                            bs.broadcastmessage(
                                "❌ Error verifying IP address.",
                                clients=[client_id],
                                transient=True,
                                color=(1, 0, 0),
                            )
                            return None  # Block command execution

                    # PASSWORD CHECK
                    if password_auth_enabled:
                        # verification check
                        # Get the player's current shortname NOW
                        try:
                            player = (
                                command.get_session_player()
                            )  # Get player using client_id
                            current_shortname = player.getname(
                                full=False, icon=False
                            )

                            # print(f"DEBUG: Checking verification for client_id={client_id}, current_shortname='{current_shortname}'") # DEBUG 4
                        except Exception as e:
                            print(
                                f"Error getting player name for verification check: {e}"
                            )
                            bs.broadcastmessage(
                                "❌ Error checking verification status.",
                                clients=[client_id],
                                color=(1, 0, 0),
                            )
                            return None  # Block command if we can't get name

                        # Check BOTH client_id existence AND if current name matches stored name
                        if not cls.is_admin_verified(
                            client_id, current_shortname
                        ):
                            # print(f"DEBUG: is_admin_verified FAILED for client_id={client_id}, name='{current_shortname}'") # DEBUG 5
                            bs.broadcastmessage(
                                f"Not verified!",
                                clients=[client_id],
                                transient=True,
                                color=(1, 0.5, 0),
                            )
                            return None  # Block command execution
                        # if we are here, verification passed
                        pass
                        # --- END VERIFICATION CHECK ---
                    # print(f"DEBUG: Executing command '{cmd}' for client_id {client_id}") # DEBUG PRINT 7
                    command()

                else:
                    # print(f"DEBUG: Client {client_id} is NOT an admin (pb-id check failed).") # DEBUG 8
                    bs.broadcastmessage(
                        "❌ Access Denied: Admins only!",
                        clients=[client_id],
                        transient=True,
                        color=(1, 0, 0),
                    )
            else:
                command()

            if not command.return_message():
                return None  # commands wont show up in chatbox
        return msg  # /<invalid_command_name> will be visible in chatbox


# CommandManager.verified_admins[113] = "HeyFang"
# print(f"DEBUG: Manually added test verification: {CommandManager.verified_admins}")
