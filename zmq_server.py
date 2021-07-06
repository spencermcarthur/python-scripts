from random import randrange
from time import sleep

import zmq

host = '127.0.0.1'
port = '5556'

context = zmq.Context()

socket = context.socket(zmq.PUB)
socket.bind(f'tcp://{host}:{port}')

while True:
    msg = str(randrange(0, 255))
    print(msg)
    socket.send(bytes(msg, 'utf-8'))
    sleep(1)
