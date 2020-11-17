from pywhale.lib.reader import MailReader
from pywhale.lib.detector import *
from pywhale.lib.indicator import Indicators
from pywhale.lib.attachments import AttachmentParser
import logging

try:
    import coloredlogs

    coloredlogs.install(level=logging.DEBUG)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
except:
    logging.basicConfig(level=logging.DEBUG)


class PyWhale:
    @staticmethod
    def process(raw_body):
        output = {
            "headers": [],
            "body": [],
            "attachments": [],
            "status": 0,
            "output_headers": {},
            "output_files": []
        }

        m = MailReader(raw_body)
        if not m:
            return output
        output['output_headers'] = m.headers

        hc = SenderHostChecker(headers=m.headers)
        if hc.test():
            output['headers'].extend(hc.reports)
            m.headers = hc.headers

        hc2 = ReplyHostChecker(headers=m.headers)
        if hc2.test():
            output['headers'].extend(hc2.reports)
            m.headers = hc2.headers

        hc3 = ToHostChecker(headers=m.headers)
        if hc3.test():
            output['headers'].extend(hc3.reports)
            m.headers = hc3.headers

        i = Indicators(mail=m)
        output['body'] = i.run()
        for x in output['headers']:
            logging.info(x)

        for x in m.attachments:
            a = AttachmentParser(attachment=x)
            results = a.process()
            output['attachments'].extend(results)
            output['output_files'].extend(a.files)
        return output
