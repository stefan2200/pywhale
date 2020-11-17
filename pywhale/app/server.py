import os.path

from flask import Flask, render_template, jsonify, request
from pywhale.whale import PyWhale


curr_file = os.path.abspath(os.path.dirname(__file__))
app_path = os.path.join(curr_file)
static_path = os.path.join(curr_file, 'static')
template_path = os.path.join(curr_file, 'templates')

app = Flask("PyWhale", root_path=app_path, template_folder=template_path)


@app.route('/', methods=['GET'])
def main():  # pragma: no cover
    return render_template("app.html")


@app.route('/api/process', methods=['POST'])
def process():  # pragma: no cover
    whale = PyWhale.process(request.form.get("body"))
    return jsonify(whale)


def start(host="127.0.0.1", port=3333):
    app.run(host=host, port=port)
