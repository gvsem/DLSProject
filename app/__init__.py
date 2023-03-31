"""
DLS Application.
"""

import os
import base64
from typing import Tuple
from flask import (
    Flask,
    Response,
    make_response,
    send_from_directory,
    request,
    flash,
    redirect
)
from app.service import (FileExplorer, Detector)
from .recognizer import Recognizer


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'tmp'
app.config['STATIC_FOLDER'] = 'static'
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'om du vill, du kan forsta allt.'

explorer = FileExplorer(FileExplorer.Config(
    dir_root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
    dir_static=app.config['STATIC_FOLDER'],
    dir_upload=app.config['UPLOAD_FOLDER']
))

recognizer = Recognizer()
detector = Detector(explorer, recognizer)


def rbg_from_hex(string: str) -> Tuple[int, int, int]:
    """Takes HEX color value and returns RGB"""
    string = string.lstrip('#')
    return tuple(int(string[i: i + 2], 16) for i in (0, 2, 4))


@app.route('/')
def index():
    """Home page."""
    return Response(
        explorer.static_content('index.html'),
        mimetype="Content-Type: text/html; charset=utf-8"
    )


@app.route('/<path:path>')
def java_script(path):
    """JavaScript files."""
    return send_from_directory(
        explorer.relative('.', explorer.attr.dir_static), 
        path
    )


@app.route('/detect-img', methods=['POST'])
def detect_img():
    """Detects people on given image."""

    def panic(message: str) -> None:
        flash(message)
        print(message)
        return redirect(request.url)

    file = request.files.get('img', None)
    if file is None:
        return panic('No file part')
    if file.filename == '':
        return panic('No selected file')

    sourcepath = explorer.upload_file(file)
    print(sourcepath)
    if not isinstance(sourcepath, str):
        return sourcepath

    threshold = int(request.values.get('threshold')) / 100.0
    color = rbg_from_hex(request.values.get('color'))

    resultpath = explorer.relative_upload('processed_' + file.filename)
    detector.process_image(sourcepath, resultpath, threshold, color)

    return make_response(explorer.content_of_binary(resultpath))
