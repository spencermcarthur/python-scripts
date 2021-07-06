from requests import get
from json import dumps, loads
from time import perf_counter

import zmq
from websockets import connect


def create_msg(market, subscribe=True):
    msg = {
            'op':      'subscribe' if subscribe else 'unsubscribe',
            'channel': 'ticker',
            'market':  market
    }

    return msg


def get_markets(currency, kind):
    url = 'https://ftx.com/api/markets'
    response = get(url)

    markets = response.json()['result']

    if currency is not None:
        markets = list(filter(lambda x: x['underlying'] == currency, markets))
    if kind is not None:
        markets = list(filter(lambda x: x['type'] == kind, markets))

    return [x['name'] for x in markets]


class FTX:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port

        self.__ws_uri = 'wss://ftx.com/ws/'
        self.__data = {}

        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.PUB)
        self.__socket.bind(f'tcp://{host}:{port}')

    async def run(self, symbols):
        async with connect(self.__ws_uri) as ws:
            for sym in symbols:
                await ws.send(dumps(create_msg(sym)))

            t = perf_counter()
            while ws.open:
                msg = loads(await ws.recv())

                t1 = perf_counter()
                await self.__handle(msg)
                print(perf_counter() - t1)

                if perf_counter() - t > 10:
                    await ws.send(dumps({'op': 'ping'}).encode())
                    t = perf_counter()

    async def __handle(self, msg: dict):
        if msg.get('channel') == 'ticker' and msg.get('type') == 'update':
            await self.__handle_ticker(msg)

    async def __handle_ticker(self, msg):
        data = msg.get('data', {})
        if not data:
            return

        bsize = data.get('bidSize')
        bprice = data.get('bid')
        aprice = data.get('ask')
        asize = data.get('askSize')

        msg_out = {
                'timestamp': data.get('time'),
                'market':        msg.get('market'),
                'bSize':         bsize,
                'bPrice':        bprice,
                'aPrice':        aprice,
                'aSize':         asize,
                'mid':           (bsize * bprice + asize * aprice) / (bsize + asize),
                'last':          data.get('last')
        }

        self.__socket.send(dumps(msg_out).encode('utf-8'))


if __name__ == '__main__':
    import asyncio

    host_ = '127.0.0.1'
    port_ = '5556'

    print(get_markets('BTC', 'future'))

    # print(f'Running FTX server on {host_}:{port_}...')
    # ftx = FTX(host_, port_)
    # asyncio.get_event_loop().run_until_complete(ftx.run(['BTC-PERP']))
