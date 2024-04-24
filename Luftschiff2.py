from pynput import keyboard
import socket
import logging


def main():
    host = "192.168.0.101"  # Use IP-address of device running server instance!!!
    # host = "localhost"  # Use this for debugging (launching client & server on same machine) only!!!
    port = 5000

    msg = ''

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:

        client_socket.connect((host, port))

        logger.debug(f"Connected to {host} {port}")

        try:

            while True:

                with keyboard.Events() as event:
                    key = event.get()
                    if key.key == keyboard.KeyCode.from_char('w'):
                        msg = 'w'
                    elif key.key == keyboard.KeyCode.from_char('a'):
                        msg = 'a'
                    elif key.key == keyboard.KeyCode.from_char('s'):
                        msg = 's'
                    elif key.key == keyboard.KeyCode.from_char('d'):
                        msg = 'd'
                    elif key.key == keyboard.KeyCode.from_char('8'):
                        msg = '8'
                    elif key.key == keyboard.KeyCode.from_char('2'):
                        msg = '2'
                    elif key.key == keyboard.Key.space:
                        msg = 'SPACE'
                    elif key.key == keyboard.KeyCode.from_char('m'):
                        msg = 'BYE'
                    elif key.key == keyboard.KeyCode.from_char('0'):
                        msg = '0'

                logger.debug(f"Sending message: {msg}")
                client_socket.send(msg.encode())

                if msg == 'BYE':
                    logger.debug("Caught message to shut down server. Shutting down client too.")
                    break

        except KeyboardInterrupt:
            logger.debug("Client interrupted. Closing connection...")

        finally:
            client_socket.close()
            logger.debug("Connection closed successfully.")


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    main()



