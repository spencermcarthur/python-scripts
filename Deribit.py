from json import dumps, loads
from time import perf_counter

import zmq
from requests import get
from websockets import connect


def create_msg(symbols, subscribe=True):
    if isinstance(symbols, str):
        symbols = [symbols]

    msg = {
            'jsonrpi': '2.0',
            'id':      3600 if subscribe else 8691,
            'method':  '/public/' + 'subscribe' if subscribe else 'unsubscribe',
            'params':  {
                    'channels': [
                            f'ticker.{sym}.raw' for sym in symbols
                    ]
            }
    }

    return msg


def get_instruments(currency, kind, expired=False):
    url = 'https://test.deribit.com/api/v2/public/get_instruments'

    params = {
            'currency': currency,
            'kind':     kind,
            'expired':  str(expired).lower()
    }

    response = get(url, params=params)

    symbols = sorted(map(lambda x: (x['instrument_name'], x['expiration_timestamp']), response.json()['result']),
                     key=lambda x: x[1])

    return [x[0] for x in symbols]


class DeribitServer:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port

        self.__ws_uri = 'wss://test.deribit.com/ws/api/v2'

        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.PUB)
        self.__socket.bind(f'tcp://{host}:{port}')

    async def run(self, symbols):
        async with connect(self.__ws_uri) as ws:
            await ws.send(dumps(create_msg(symbols)))

            t = perf_counter()
            while ws.open:
                msg = loads(await ws.recv())

                await self.__handle(msg)

                # heartbeat
                if perf_counter() - t > 10:
                    await ws.pong()
                    t = perf_counter()

    async def __handle(self, msg: dict):
        if 'ticker' in msg.get('params', {}).get('channel', ''):
            await self.__handle_ticker(msg)

    async def __handle_ticker(self, msg: dict):
        data = msg.get('params', {}).get('data', {})
        if not data:
            return

        bsize = data.get('best_bid_amount')
        bprice = data.get('best_bid_price')
        aprice = data.get('best_ask_price')
        asize = data.get('best_ask_amount')

        msg_out = {
                'timestamp':     data.get('timestamp'),
                'symbol':        data.get('instrument_name'),
                'bSize':         bsize,
                'bPrice':        bprice,
                'aPrice':        aprice,
                'aSize':         asize,
                'mid':           (bsize * bprice + asize * aprice) / (bsize + asize),
                'last':          data.get('last_price')
        }

        self.__socket.send(dumps(msg_out).encode('utf-8'))


if __name__ == '__main__':
    import asyncio

    host_ = '127.0.0.1'
    port_ = '5556'

    print(get_instruments('BTC', 'future'))

    # print(f'Running Deribit server on {host_}:{port_}...')
    # db = DeribitServer(host_, port_)
    # asyncio.get_event_loop().run_until_complete(db.run(get_instruments('BTC', 'future')))
