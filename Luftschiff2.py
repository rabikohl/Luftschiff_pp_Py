from pynput import keyboard
import socket


host = "localhost"
port = 5000

msg = ''

s = socket.socket()
s.connect((host, port))






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
            break
        elif key.key == keyboard.KeyCode.from_char('0'):
            msg = '0'
    s.send(msg.encode())
