import re
import base64
import validators
import tldextract


class HeaderChecker:
    header = None
    headers = {

    }
    reports = [

    ]

    opts = {

    }
    #report = {"header": "From", "indicator": "danger", "data": "From name contains uncommon HTML symbols"}

    def __init__(self, headers={}):
        self.headers = headers
        self.reports = []

    def test(self):
        if self.header in self.headers:
            self.check()
            return True
        return False

    def check(self):
        print("You should override this!!")
        return None

    def header_decode(self, header):
        if "=?" not in header:
            return header

        for h in re.findall(r'(=\?.+?\?=)', header):
            parts = h.split('?')
            enc_type = parts[2]
            body = parts[3]
            if enc_type.lower() == "b":
                body = base64.b64decode(body).decode()
            header = header.replace(h, body)
        return header

    def close(self):
        self.reports = []


class ReplyHostChecker(HeaderChecker):
    header = "Return-Path"

    def check(self):
        value = self.headers[self.header]
        return_domain = None
        from_domain = None
        if "<" in value and ">" in value:
            value = value.replace('<', '').replace('>', '')
        if "@" in value:
            value = value.split("@")[1]
        if not validators.domain(value.lower().strip()):
            self.reports.append({
                "header": self.header,
                "indicator": "warning",
                "data": "Unable to parse return domain: %s" % (value)
            })
        else:
            return_domain = value.lower().strip()

        if "From" in self.headers:
            get_email = re.search(r'<(.+?)>', self.headers['From'])
            if get_email:
                email = get_email.group(1)
                if not validators.domain(email.split('@')[1].lower().strip()):
                    self.reports.append({
                        "header": self.header,
                        "indicator": "warning",
                        "data": "Unable to parse FROM address domain: %s" % (email.split('@')[1])
                    })
                else:
                    from_domain = email.split('@')[1].lower().strip()
        if from_domain and return_domain:
            from_domain = tldextract.extract(from_domain)
            return_domain = tldextract.extract(return_domain)
            if from_domain.domain != return_domain.domain or from_domain.suffix != return_domain.suffix:
                self.reports.append({
                    "header": self.header,
                    "indicator": "warning",
                    "data": "From root domain %s is not part of return root domain: %s" % (from_domain, return_domain)
                })
        return True


class ToHostChecker(HeaderChecker):
    header = "To"

    def check(self):
        value = self.headers[self.header]
        to_addrs = []
        if "," in value:
            to_addrs = [x.lower().strip() for x in value.split(',')]
        else:
            to_addrs = [value.lower().strip()]
        if "delivery_addr" in self.opts and self.opts['delivery_addr'] not in to_addrs:
            self.reports.append({
                "header": self.header,
                "indicator": "warning",
                "data": "To address %s does not contain: %s" % (value, self.opts['delivery_addr'])
            })
        if len(to_addrs) > 10:
            self.reports.append({
                "header": self.header,
                "indicator": "warning",
                "data": "To address line contains %d entries, this might indicate mass-mail" % (len(to_addrs))
            })


class SenderHostChecker(HeaderChecker):
    header = "From"

    def check(self):
        value = self.headers[self.header]
        email = None
        name = None
        get_email = re.search(r'(.+?)\s*<(.+?)>', value)
        if get_email:
            email = get_email.group(2)
            name = get_email.group(1)
            if name.startswith('"') and name.endswith('"'):
                name = name[1:-1]
        else:
            email = value

        if name:
            esc_name = name.encode('ascii', errors='ignore').decode()
            if esc_name != name:
                self.reports.append({
                    "header": self.header,
                    "indicator": "warning",
                    "data": "Name %s contains special characters, real: %s" % (name, esc_name)
                })

            dec = self.header_decode(esc_name)
            if dec != esc_name:
                self.reports.append({
                    "header": self.header,
                    "indicator": "warning",
                    "data": "Name %s mixed encoding was applied, real: %s" % (esc_name, dec)
                })
                if "@" in dec and email not in dec:
                    self.reports.append({
                        "header": self.header,
                        "indicator": "danger",
                        "data": "Encoded text: %s contains an email but does not contain the from email: %s" % (
                        dec, email)
                    })
            if '\u200e' in dec:
                dec = dec.replace('\u200e', '')
                self.reports.append({
                    "header": self.header,
                    "indicator": "danger",
                    "data": "Text: %s contains &lrm; (Left-to-Right) character" % (
                    dec)
                })

            if "@" in esc_name and email not in esc_name:
                self.reports.append({
                    "header": self.header,
                    "indicator": "danger",
                    "data": "Name text: %s contains an email but does not contain the from email: %s" % (esc_name, email)
                })
            if dec:
                self.headers['stripped_from'] = dec
            if esc_name:
                self.headers['unescaped_from'] = esc_name

        return True
