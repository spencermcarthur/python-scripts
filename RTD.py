from pyxll import RTD

import zmq


class DeribitClient(RTD):
    def __init__(self):
        super(DeribitClient, self).__init__(value=0.)

        self.__stopped = False

    async def connect(self):
        while not self.__stopped:
            pass

    async def disconnect(self):
        self.__stopped = True


