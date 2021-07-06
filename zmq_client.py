import zmq

from json import loads
from time import sleep

host = '127.0.0.1'
port = '5556'

context = zmq.Context()
context.setsockopt(zmq.SUBSCRIBE, b"")

socket = context.socket(zmq.SUB)
socket.connect(f'tcp://{host}:{port}')

while True:
    msg = loads(socket.recv().decode())

    print(msg['timestamp'])

    # data = msg.get('params', {}).get('data', {})
    # if data.get('instrument_name', '') == 'BTC-PERPETUAL':
    #     print(data.get('best_bid_price', ''), '/', data.get('best_ask_price', ''))

    # if msg.get('symbol') == 'BTC-PERPETUAL':
    #     print(msg.get('last'))
