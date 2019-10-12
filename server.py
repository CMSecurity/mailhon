import asyncio
import logging

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Sink
from aiosmtpd.smtp import SMTP as Server, syntax


class CustomHostnameController(Controller):
    def factory(self):
        return Server(self.handler, hostname='mailhon.serv.local', ident="Exim 420")


async def amain(loop):
    # TODO: Add custom handlers for DATA and stuff (i.e. RCP)
    # see https://aiosmtpd.readthedocs.io/en/latest/aiosmtpd/docs/controller.html#using-the-controller
    # and handlers: https://aiosmtpd.readthedocs.io/en/latest/aiosmtpd/docs/handlers.html#handler-hooks
    cont = CustomHostnameController(Sink(),port=8025)
    cont.start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.create_task(amain(loop=loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
