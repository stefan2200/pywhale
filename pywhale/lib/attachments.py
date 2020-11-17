import re
import json
import os
import logging
from io import BytesIO
import zipfile

from pywhale.lib.utils import Utils


# Module for parsing email attachments
class AttachmentParser:

    attachment = None

    indicators = []
    directory = None
    merged_links = [

    ]
    logger = logging.getLogger("Attachments")
    files = []

    def __init__(self, attachment, indicator_directory=None):
        self.attachment = attachment
        self.directory = indicator_directory
        if not self.directory:
            self.directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../", "attachments")
        self.load_indicators()

    def load_indicators(self):
        self.indicators = []
        for i_file in os.listdir(self.directory):
            full_path = os.path.join(self.directory, i_file)
            try:
                with open(full_path, 'r') as f:
                    indicator = json.load(f)
                    if indicator not in self.indicators:
                        self.indicators.append(indicator)
            except Exception as e:
                self.logger.error("Error loading script %s: %s" % (full_path, str(e)))
        self.logger.debug("Loaded %d attachment scripts" % len(self.indicators))

    def unzip(self, data):
        if type(data) == str:
            data = data.encode()
        f = BytesIO(data)
        try:
            zf = zipfile.ZipFile(f, 'r')
            out_stream = []
            for zfile in zf.infolist():
                out_stream.append({"name": zfile.filename, "body": zf.read(zfile)})
        except Exception as e:
            self.logger.error("Error reading zipped file data: %s" % str(e))
            return []
        return out_stream

    def run_indicators(self, indicators, body):
        results = []
        body_bytes = type(body) is not str
        for i in indicators:
            if 'type' in i:
                match = Utils.contains(needle=i['needles'], haystack=body, search_type=i['type'])
                if match:
                    results.append({
                        "match": match,
                        "indicator": i['indicator'],
                        "output": i['output']
                    })

        return results

    def run_file_indicators(self, indicators, filename, parent):
        results = []
        for i in indicators:
            match = Utils.contains(needle=i['needles'], haystack=filename, search_type=i['type'])
            if match:
                results.append({
                 "location": filename,
                  "match": match,
                  "name": parent['name'],
                  "indicator": i['indicator'],
                  "output": i['output']
                })

        return results

    def run_script(self, script):
        output = []
        body = [{"name": self.attachment['filename'], "body": self.attachment['body']}]
        self.logger.info("Processing attachment %s with script %s" % (self.attachment['filename'], script['name']))

        # unzip with BytesIO
        if script['decoder'] == "zip":
            zipdata = self.unzip(self.attachment['body'])
            for f in zipdata:
                body.append(f)
            self.logger.debug("Found %d files in zipfile: %s" % (len(body), self.attachment['filename']))

        # scan one or multiple file bodies for strings
        for f in body:
            self.files.append({"name": f['name'], "length": len(f['body']), "parent": self.attachment['filename']})
            results = self.run_indicators(script['indicators'], f['body'])
            if results:
                for r in results:
                   output.append({
                       "attachment": self.attachment['filename'],
                       "location": f['name'],
                       "match": r
                   })
            # for scanning zipped files
            if 'files' in script:
                results = self.run_file_indicators(script['files'], f['name'], parent=script)
                if results:
                    for r in results:
                        output.append({
                            "key": self.attachment['filename'],
                            "location": f['name'],
                            "match": r
                        })
        return output

    def process(self):
        full_output = []
        for script in self.indicators:
            matches = [script['file_type']] if type(script['file_type']) == str else script['file_type']
            for m_type in matches:
                if self.attachment['filename'].lower().endswith(m_type):
                    result = self.run_script(script)
                    if result:
                        full_output.extend(result)
        return full_output
