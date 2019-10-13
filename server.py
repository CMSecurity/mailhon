import asyncio
import logging
from datetime import datetime, timezone

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Sink
from aiosmtpd.smtp import SMTP as Server, syntax


class CustomHostnameController(Controller):
    def factory(self):
        full_ident = 'ESMTP Exim 4.84_2 %s' % datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
        return Server(self.handler, data_size_limit=52428800, hostname='mailhon.serv.local', ident=full_ident)

class HoneyHandler:
    async def handle_HELO(self, server, session, envelope, hostname):
        print('Incoming hostname: %s' % hostname)
        session.host_name = hostname
        return '250 {}'.format(server.hostname)

    async def handle_EHLO(self, server, session, envelope, hostname):
        print('Incoming hostname: %s' % hostname)
        session.host_name = hostname
        await server.push('250-PIPELINING')
        return '250 HELP'

    async def handle_VRFY(self, server, session, envelope, address):
        print('Client tried to verify address: %s' % address)

    async def handle_DATA(self, server, session, envelope):
        print('Message from %s' % envelope.mail_from)
        print('Message for %s' % envelope.rcpt_tos)
        print('Message data:\n')
        print(envelope.content.decode('utf8', errors='replace'))
        print('End of message')
        return '250 Message accepted for delivery'


async def amain(loop):
    cont = CustomHostnameController(HoneyHandler(), hostname='', port=8026)
    cont.start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.create_task(amain(loop=loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
