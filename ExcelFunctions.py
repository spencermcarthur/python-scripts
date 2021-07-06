from pyxll import xl_func

import Deribit


@xl_func
def deribit_btc_futures_contracts():
    return [Deribit.get_instruments('BTC', 'future')]


@xl_func
def deribit_eth_futures_contracts():
    return [Deribit.get_instruments('ETH', 'future')]
