import base64
import re
import logging
from pywhale.lib.html_processor import HTMLBody


# Class for reading email segments
class MailReader:
    links = []
    sender = (None, None)
    server = None
    body = ""

    headers = {

    }

    attachments = {

    }

    data = {

    }

    bodies = [

    ]
    header_regex = re.compile(r'^[A-Z][\w-]+:\s')
    logger = logging.getLogger("MailParser")

    def __init__(self, body):

        body = body.decode('utf-8') if type(body) is not str else body

        rbody = body.split('\n\n')
        headers = rbody[0]
        raw_body = '\n\n'.join(rbody[1:]).strip()
        self.headers = self.get_headers(headers)
        self.attachments = {}

        if "Content-Type" not in self.headers:
            self.logger.error("Invalid email!!!")
            return None

        ctype = self.headers['Content-Type']
        self.logger.info("Parsing mail body with Content-Type: %s" % ctype)
        if "multipart/" in ctype:
            boundary = re.search(r'boundary="(.+?)"', ctype)
            if boundary:
                self.data, self.attachments = self.mixed_read(boundary.group(1), raw_body)

        if "text/html" in ctype:
            self.data = [
                {
                    "type": ctype,
                    "body": raw_body
                }
            ]
            self.bodies.append(HTMLBody(raw_body))

        self.logger.info("Email parsed: %d content parts; %d attachments" % (len(self.data), len(self.attachments)))

    def mixed_read(self, boundary, text):
        # part = {"type":"", "encoding":"", "charset":"", "body":""}
        parts = []
        attachments = []
        marker = "--%s" % boundary.strip()
        # strip first / last one
        content_parts = text.split(marker)[1:-1]
        for p in content_parts:
            header = p.split("\n\n")[0].strip()
            body = "\n\n".join(p.split("\n\n")[1:])
            hparts = self.get_headers(header)
            ctype = hparts['Content-Type'].split(';')[0].strip() if 'Content-Type' in hparts else None
            cset = hparts['Content-Type'].split(';')[1].strip() if 'Content-Type' in hparts and ";" in hparts['Content-Type'] else None
            alt = []
            if ctype == "multipart/alternative":
                alt_boundary = re.search(r'boundary="(.+?)"', hparts['Content-Type'])
                if alt_boundary:
                    alt, alt_attachments = self.mixed_read(alt_boundary.group(1), text)
                    if len(alt_attachments):
                        attachments.extend(alt_attachments)
                    body = None
            enc = None
            if 'Content-Transfer-Encoding' in hparts:
                enc = hparts['Content-Transfer-Encoding']
                if enc == "base64":
                    body = base64.b64decode(body)

            if 'Content-Disposition' in hparts:
                dispos = hparts['Content-Disposition']
                if "attachment;" in dispos:
                    fname = re.search('filename="(.+?)"', dispos)
                    if not fname:
                        fname = None
                    else:
                        fname = fname.group(1)
                    attachment = {
                        "filename": fname,
                        "type": ctype,
                        "charset": cset,
                        "encoding": enc,
                        "body": body
                    }
                    if attachment not in attachments:
                        attachments.append(attachment)
                    continue

            part = {
                "type": ctype,
                "charset": cset,
                "encoding": enc,
                "body": body,
                "alt": alt
            }

            parts.append(part)
            if body and len(body) and "text/html" in ctype:
                parsed = HTMLBody(body)
                self.bodies.append(parsed)

        return parts, attachments

    def get_headers(self, raw):
        headers = {

        }
        tmp = ""
        tmpkey = ""
        for h in raw.strip().split("\n"):
            if self.header_regex.search(h):
                if tmpkey:
                    headers[tmpkey] = tmp
                    tmpkey = None
                kvalue = h.split(": ")
                tmpkey = kvalue[0]
                tmp = ": ".join(kvalue[1:])
            else:
                tmp += h
        headers[tmpkey] = tmp

        return headers




