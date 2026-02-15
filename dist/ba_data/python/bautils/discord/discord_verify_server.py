# Released under the MIT License. See LICENSE for details.
#
"""socket for server utils provided by this project."""

# ba_meta require api 9

# print("!!! LOADING discord_verify_server.py !!!")
# Add these imports at the top
import socket
import threading
import os
import json
import babase as ba

# import settings
try:
    from .. import settings
except ImportError:
    print(
        "\nERROR: discord_verify_server.py could not import settings.py."
        " Discord integration will be disabled."
    )

    class DummySettings:
        enableDiscordIntegration = False

    settings = DummySettings()

# Make sure this import points to your CommandManager class
# Adjust the path if necessary (e.g., from .chat import CommandManager)
try:
    from ..chat.cmd_manager import CommandManager
except ImportError:
    print("ERROR: Could not import CommandManager for Unix socket server.")
    # Handle the error appropriately - maybe disable the feature
    CommandManager = None  # Prevent crashes later


# MUST match the path used in your Discord bot
SOCKET_PATH = '/tmp/bombsquad_verify.sock'


def handle_socket_connection(client_sock: socket.socket) -> None:
    """Handles a single connection from the Discord bot."""
    # print(f"Socket Server: Connection received from bot.")
    data_buffer = b''
    try:
        # Receive data in chunks (basic example, might need refinement for large messages)
        while True:
            chunk = client_sock.recv(1024)
            if not chunk:
                break  # Connection closed by client
            data_buffer += chunk
            # Basic check: assume a complete JSON message ends with '}'
            if data_buffer.endswith(b'}'):
                break

        if not data_buffer:
            print("Socket Server: Received empty data. Closing connection.")
            return

        # Decode and parse the JSON data
        message = data_buffer.decode('utf-8')
        # print(f"Socket Server: Received raw data: {message}")
        data = json.loads(message)

        # Process the request
        action = data.get('action')
        client_id = data.get('client_id')
        shortname = data.get('shortname')

        response = "ERROR: Invalid request"  # Default response

        if (
            action == 'verify_admin'
            and isinstance(client_id, int)
            and isinstance(shortname, str)
        ):
            # print(f"Socket Server: Processing verify_admin for client_id={client_id}, shortname='{shortname}'")

            # --- CRITICAL: Use ba.pushcall to interact with BombSquad ---
            # We define a helper function to run in the main thread
            # This is necessary because CommandManager interacts with game state
            # FIXME: thread still running at python shutdown!
            def _verify_in_main_thread():
                if CommandManager:
                    success = CommandManager.mark_admin_verified(
                        client_id, shortname
                    )
                    # We can't easily get the 'success' bool back to *this* thread
                    # So we just assume success if the call is made for the response
                    # A more complex setup could use queues or callbacks
                else:
                    print("Socket Server Error: CommandManager not imported.")

            ba.pushcall(_verify_in_main_thread, from_other_thread=True)

            response = "OK"  # Assume OK for now (simplest response)
            # print(f"Socket Server: Verification pushed to main thread for client_id={client_id}.")

        else:
            print(f"Socket Server: Invalid action or data received: {data}")
            response = "ERROR: Invalid action or data format"

        # Send response back to the bot
        client_sock.sendall(response.encode('utf-8'))
        print(f"Socket Server: Sent response '{response}' to bot.")

    except json.JSONDecodeError:
        print(
            f"Socket Server: Error decoding JSON: {data_buffer.decode('utf-8', errors='ignore')}"
        )
        client_sock.sendall(b"ERROR: Invalid JSON")
    except ConnectionResetError:
        print("Socket Server: Connection reset by peer.")
    except Exception as e:
        print(f"Socket Server: Error handling connection: {e}")
        try:
            client_sock.sendall(
                f"ERROR: Server exception - {type(e).__name__}".encode('utf-8')
            )
        except:
            pass  # Ignore errors sending error message back
    finally:
        print("Socket Server: Closing client connection.")
        client_sock.close()


def start_unix_socket_server() -> None:
    """Creates and runs the Unix Domain Socket server loop."""
    # Ensure CommandManager was imported
    if not CommandManager:
        print(
            "Unix Socket Server cannot start: CommandManager failed to import."
        )
        return

    # Cleanup existing socket file if it exists
    if os.path.exists(SOCKET_PATH):
        print(f"Socket Server: Removing existing socket file at {SOCKET_PATH}")
        try:
            os.unlink(SOCKET_PATH)
        except OSError as e:
            print(f"Socket Server: Error removing socket file: {e}. Exiting.")
            return

    # Create the Unix socket
    server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        # Bind the socket to the path
        print(f"Socket Server: Binding to socket path {SOCKET_PATH}...")
        server_sock.bind(SOCKET_PATH)

        # Listen for incoming connections (allow a small backlog)
        server_sock.listen(5)
        print(f"Socket Server: Listening on {SOCKET_PATH}...")

        while True:
            # Wait for a connection
            # print("Socket Server: Waiting for connection...")
            try:
                client_connection, client_address = server_sock.accept()
                # Handle each connection in a new thread so we can accept others
                # Use daemon=True so these threads don't block server exit
                handler_thread = threading.Thread(
                    target=handle_socket_connection,
                    args=(client_connection,),
                    daemon=True,
                )
                handler_thread.start()
            except ConnectionAbortedError:
                print(
                    "Socket Server: Accept loop aborted (server likely shutting down)."
                )
                break  # Exit loop if socket is closed externally
            except Exception as e:
                print(f"Socket Server: Error accepting connection: {e}")
                # Maybe add a small sleep here to prevent spamming errors

    except OSError as e:
        print(f"Socket Server: Failed to bind or listen on {SOCKET_PATH}: {e}")
    except Exception as e:
        print(f"Socket Server: Unexpected error in server loop: {e}")
    finally:
        # Cleanup the socket file when the server loop ends/crashes
        print("Socket Server: Shutting down and cleaning up socket file.")
        server_sock.close()
        if os.path.exists(SOCKET_PATH):
            try:
                os.unlink(SOCKET_PATH)
            except OSError as e:
                print(
                    f"Socket Server: Error removing socket file on shutdown: {e}"
                )


# --- Starting the Server Thread ---

# You need to call this function *once* when your server starts.
# Example: Put this at the end of your main server script or in an init function.

# --- CONDITIONAL THREAD START ---
# Check the setting from the imported settings module
if getattr(settings, 'enableDiscordIntegration', False):
    print(
        "Discord integration enabled in settings. Starting Unix Socket Server thread..."
    )
    socket_server_thread = threading.Thread(
        target=start_unix_socket_server, daemon=True
    )
    socket_server_thread.start()
    print("Unix Socket Server thread started.")
else:
    print(
        "Discord integration disabled in settings. Unix Socket Server will not start."
    )
# --------------------------------

# --- Optional: Cleanup on Server Exit ---
# If your server has a specific shutdown hook, you might want to explicitly
# close the server socket and remove the file there too, although the daemon
# thread and the finally block should handle most cases.
# import atexit
# def cleanup_socket():
#     if os.path.exists(SOCKET_PATH):
#         try: os.unlink(SOCKET_PATH)
#         except OSError: pass
# atexit.register(cleanup_socket)
