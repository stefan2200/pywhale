import json
import os
import logging
import re
from urllib.parse import urlparse


class Indicators:
    indicators = []
    directory = None
    mail = None
    merged_links = [

    ]
    merged_images = [

    ]
    logger = logging.getLogger("Indicators")

    def __init__(self, mail, indicator_directory=None):
        self.mail = mail
        self.directory = indicator_directory
        if not self.directory:
            self.directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../", "indicators")
        self.load_indicators()

    def load_indicators(self):
        for i_file in os.listdir(self.directory):
            full_path = os.path.join(self.directory, i_file)
            try:
                with open(full_path, 'r') as f:
                    indicator = json.load(f)
                    if indicator not in self.indicators:
                        self.indicators.append(indicator)
            except Exception as e:
                self.logger.error("Error loading script %s: %s" % (full_path, str(e)))
        self.logger.debug("Loaded %d indicator scripts" % len(self.indicators))

    def read_from(self):
        if 'stripped_name' in self.mail.headers:
            return self.mail.headers['stripped_name']
        if 'unescaped_name' in self.mail.headers:
            return self.mail.headers['unescaped_name']
        if "<" in self.mail.headers['From']:
            return self.mail.headers['From'].split('<')[1].split('>')[0]
        return self.mail.headers['From']

    def match_link(self, text, match_type="contains", options=None, allowed_hosts=[]):
        matched_links = []
        if not options:
            options = []
        for link in self.merged_links:
            href = link['href']
            link_text = link['text']
            if "lowercase" in options:
                href = href.lower()
                link_text = link_text.lower()
            if match_type == "contains":
                if text in href or text in link_text:
                    try:
                        good = 0
                        u = urlparse(href)
                        for h in allowed_hosts:
                            if u.netloc.endswith(h):
                                good = 1
                        if good:
                            continue
                    except:
                        continue
                    matched_links.append(link)
        return matched_links

    def run_indicator(self, i):
        results = []
        for sub in i['indicators']:
            if sub['target'] == "link":
                for match in sub['matches']:
                    out = self.match_link(
                        match['match'],
                        match_type=match['type'] if 'type' in match else 'contains',
                        options=match['options'],
                        allowed_hosts=i['hosts'] if 'hosts' in i else []
                    )
                    if out:
                        for matched_link in out:
                            results.append(
                                {"name": i['name'],
                                 "data": matched_link,
                                 "indicator": sub['indicator'],
                                 "target": sub['target'],
                                 "match": match,
                                 "output": sub['type']})
            if sub['target'] == "body":
                for match in sub['matches']:
                    out = self.match_link(
                        match['match'],
                        match_type=match['type'] if 'type' in match else 'contains',
                        options=match['options'],
                        allowed_hosts=i['hosts'] if 'hosts' in i else []
                    )
                    if out:
                        for matched_link in set(out):
                            results.append({"name": i['name'],
                                            "data": matched_link,
                                            "indicator": sub['indicator'],
                                            "target": sub['target'],
                                            "match": match,
                                            "type": sub['type']})
            return results

    def image_check(self):
        output = []
        for img in self.merged_images:
            if img.startswith('\\\\'):
                output.append({'data': {'href': img}, "output": "Image contains SMB path, probably NTLM sniffer", "indicator": "danger", "name": "NTLM sniffing"})
            if img.startswith('http') and '?' in img:
                output.append({'data': {'href': img}, "output": "Image contains remote URL with parameters, probably click callback", "indicator": "warning", "name": "HTTP callback"})
        return output

    def run(self):
        results = []
        for b in self.mail.bodies:
            if not b.parsed:
                continue
            for link in b.links:
                if link not in self.merged_links:
                    self.merged_links.append(link)
            for src in b.images:
                if src not in self.merged_images:
                    self.merged_images.append(src)
            results.extend(self.image_check())
        for indicator in self.indicators:
            res = self.run_indicator(indicator)
            if res:
                results.extend(res)
        return results
