# -*- coding: utf-8 -*-
import io
import json
import os

from PIL import Image
from flask import Flask, flash, request, redirect, url_for, Response, make_response, send_from_directory
from torchvision import transforms
from werkzeug.utils import secure_filename

import cProfile

pr = cProfile.Profile()
pr.enable()


UPLOAD_FOLDER = './tmp/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def root_dir():
    return os.path.abspath(os.path.dirname(__file__))

def get_file(filename, charset='utf-8'):
    src = os.path.join(root_dir(), filename)
    with open(src, 'r', encoding=charset) as f:
        return f.read()
#
# def get_file(filename):
#
#     try:
#         src = os.path.join(root_dir(), filename)
#         with open(src, 'r') as f:
#             return f.read().decode('utf-8')
#         #return open(src).read()
#     except IOError as exc:
#         return str(exc)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'om du vill, du kan forsta allt.'
app.config['SESSION_TYPE'] = 'filesystem'

def upload_file():
    if request.method == 'POST':
        INPUT_NAME = 'img'
        if INPUT_NAME not in request.files:
            flash('No file part')
            print('no file part')
            return redirect(request.url)
        file = request.files[INPUT_NAME]
        if file.filename == '':
            flash('No selected file')
            print('no sel part')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return os.path.join(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    content = get_file('static/index.html')
    return Response(content, mimetype="Content-Type: text/html; charset=utf-8")


import torchvision

model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)

import cv2
import torch

def detect_boxes(model, img_path, CONF_THRESH=0.8):

    model = model.eval()
    img_numpy = Image.open(img_path)
    img = transforms.ToTensor()(img_numpy)
    img2 = torch.from_numpy(cv2.imread(img_path)[:,:,::-1].astype('float32')).permute(2,0,1)

    print(img.shape)
    print(img2.shape)

    img = img / 255.

    predictions = model(img[None,...])
    return predictions[0]['boxes'][predictions[0]['scores'] > CONF_THRESH].detach().numpy().astype(int).tolist()

@app.route('/<path:path>')
def send_js(path):
    print( path)
    return send_from_directory('./static', path)

@app.route('/detect-img',methods=['POST'])
def detect_1():

    fn = upload_file()

    if not(type(fn) == str):
        return fn

    r = detect_boxes(model, fn)
    #print(r)
    return Response(json.dumps(r), mimetype="text/json")


if __name__ == '__main__':
    app.run()
