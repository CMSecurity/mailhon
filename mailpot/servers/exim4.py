import asyncio
import logging
from datetime import datetime, timezone

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Sink
from aiosmtpd.smtp import SMTP as Server, syntax

from servers.logger import Logger


log = Logger()

class HoneyExim(Server):
    EMPTYBYTES = b''
    MISSING = object()

    @syntax('EHLO hostname')
    async def smtp_EHLO(self, hostname):
        if not hostname:
            await self.push('501 Syntax: EHLO hostname')
            return
        self._set_rset_state()
        self.session.extended_smtp = True
        await self.push('250-%s Hello %s [%s]' % (self.hostname, hostname, self.session.peer[0]))
        if self.data_size_limit:
            await self.push('250-SIZE %s' % self.data_size_limit)
            self.command_size_limits['MAIL'] += 26
        if not self._decode_data:
            await self.push('250-8BITMIME')
        if self.enable_SMTPUTF8:
            await self.push('250-SMTPUTF8')
            self.command_size_limits['MAIL'] += 10
        if self.tls_context and not self._tls_protocol:
            await self.push('250-STARTTLS')
        status = await self._call_handler_hook('EHLO', hostname)
        if status is self.MISSING:
            self.session.host_name = hostname
            status = '250 HELP'
        await self.push(status)

    @syntax('DATA')
    async def smtp_DATA(self, arg):
        if not self.session.host_name:
            await self.push('503 Error: send HELO first')
            return
        if not self.envelope.rcpt_tos:
            await self.push('503 Error: need RCPT command')
            return
        if arg:
            await self.push('501 Syntax: DATA')
            return
        await self.push('354 Enter message, ending with "." on a line by itself')
        data = []
        num_bytes = 0
        size_exceeded = False
        while self.transport is not None:           # pragma: nobranch
            try:
                line = await self._reader.readline()
            except asyncio.CancelledError:
                self._writer.close()
                raise
            if line == b'.\r\n':
                break
            num_bytes += len(line)
            if (not size_exceeded and
                    self.data_size_limit and
                    num_bytes > self.data_size_limit):
                size_exceeded = True
                await self.push('552 Error: Too much mail data')
            if not size_exceeded:
                data.append(line)
        if size_exceeded:
            self._set_post_data_state()
            return
        # Remove extraneous carriage returns and de-transparency
        # according to RFC 5321, Section 4.5.2.
        for i in range(len(data)):
            text = data[i]
            if text and text[:1] == b'.':
                data[i] = text[1:]
        content = original_content = self.EMPTYBYTES.join(data)
        if self._decode_data:
            if self.enable_SMTPUTF8:
                content = original_content.decode(
                    'utf-8', errors='surrogateescape')
            else:
                try:
                    content = original_content.decode('ascii', errors='strict')
                except UnicodeDecodeError:
                    # This happens if enable_smtputf8 is false, meaning that
                    # the server explicitly does not want to accept non-ascii,
                    # but the client ignores that and sends non-ascii anyway.
                    await self.push('500 Error: strict ASCII mode')
                    return
        self.envelope.content = content
        self.envelope.original_content = original_content

        status = await self._call_handler_hook('DATA')

        self._set_post_data_state()
        await self.push('250 OK' if status is self.MISSING else status)


class HoneyEximHandler:
    async def handle_HELO(self, server, session, envelope, hostname):
        log.info(session, "mailhon.helo", hostname=hostname)
        session.host_name = hostname
        return '250 {}'.format(server.hostname)

    async def handle_EHLO(self, server, session, envelope, hostname):
        log.info(session, "mailhon.ehlo", hostname=hostname)
        session.host_name = hostname
        await server.push('250-PIPELINING')
        return '250 HELP'

    # async def handle_VRFY(self, server, session, envelope, address):
    #     log.info(session, "mailhon.vrfy", address=address)

    # async def handle_MAIL(self, server, session, envelope, address, mail_options):
    #     log.info(session, "mailhon.mail_from", address=address)
    #     envelope.mail_from = str(address)

    # async def handle_RCPT(self, server, session, envelope, address, options):
    #     log.info(session, "mailhon.rcpt", address=address)
    #     envelope.rcpt_tos.append(address)
    #     return '250 Accepted'


    async def handle_DATA(self, server, session, envelope):
        log.info(session, "mailhon.data", envelope_from=envelope.mail_from, envelope_to=envelope.rcpt_tos, envelope_data=envelope.content.decode('utf8', errors='replace'))
        return '250 OK' # TODO: Exim returns "250 OK id=MESSAGE_ID"
        # see https://www.exim.org/exim-html-current/doc/html/spec_html/ch-how_exim_receives_and_delivers_mail.html


class HoneyEximController(Controller):
    def factory(self):
        full_ident = 'ESMTP Exim 4.84_2 %s' % datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
        return HoneyExim(self.handler, data_size_limit=52428800, hostname='mailhon.serv.local', ident=full_ident)
