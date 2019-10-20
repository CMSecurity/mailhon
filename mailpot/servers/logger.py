import json
import logging

class StructuredMessage(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __str__(self):
        return '%s' % (json.dumps(self.kwargs))


class Logger():
    is_initialized = False
    _ = StructuredMessage
    def __init__(self):
        if not Logger.is_initialized:
            # logging.basicConfig(level=logging.INFO, format='%(message)s')
            Logger.is_initialized = True
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)

            fh = logging.FileHandler("mails.json")
            fh.setLevel(logging.WARNING)

            ch = logging.StreamHandler()
            ch.setLevel(logging.CRITICAL)

            formatter = logging.Formatter("%(message)s")
            fh.setFormatter(formatter)

            logger.addHandler(ch)
            logger.addHandler(fh)


    def info(self, session, eventid, **kwargs):
            logging.warn(Logger._(src_ip=session.peer[0], src_port=session.peer[1], eventid=eventid, **kwargs))
