import asyncio
import logging
from datetime import datetime, timezone

from servers.exim4 import HoneyEximController, HoneyEximHandler


async def amain(loop):
    cont = HoneyEximController(HoneyEximHandler(), hostname='', port=8025)
    cont.start()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(amain(loop=loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
