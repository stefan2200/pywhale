import optparse
import json
import sys

import pywhale.app.server
from pywhale.whale import *


def main():
    parser = optparse.OptionParser()
    parser.add_option("-e", "--email-file", default=None, help="The email body to parse, none will start server", dest="mail")
    parser.add_option("-o", "--output-file", default=None, help="File to write output to (only works with -e)", dest="output")
    parser.add_option("-p", "--port", default=3333, type="int", help="The port to start the server on", dest="port")
    parser.add_option("-s", "--host", default="127.0.0.1", help="The host to start the server on (127.0.0.1 by default)", dest="host")

    options, args = parser.parse_args()

    if options.mail:
        with open(options.mail, 'r') as input_file:
            data = input_file.read()
            if not data:
                print("Error reading email")
                sys.exit(-1)
            results = PyWhale().process(raw_body=data)
            if not results:
                print("Error parsing email")
                sys.exit(-1)
            if options.output:
                with open(options.output, 'w') as output_file:
                    json.dump(obj=results, fp=output_file)
    else:
        pywhale.app.server.start(host=options.host, port=options.port)


if __name__ == "__main__":
    main()