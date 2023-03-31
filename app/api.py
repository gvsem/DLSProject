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
    return send_from_directory('./static', path)


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

    filepath = explorer.upload_file(file)
    if not isinstance(filepath, str):
        return filepath

    threshold = int(request.values.get('threshold')) / 100.0
    color = rbg_from_hex(request.values.get('color'))

    resultpath = detector.process_image(filepath, threshold, color)

    return make_response(base64.b64encode(
        explorer.content_of(resultpath, mode='b')
    ))
