# -*- coding: utf-8 -*-
import io
import json
import os
from flask import Flask, flash, request, redirect, url_for, Response, make_response, send_from_directory
from werkzeug.utils import secure_filename

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
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor

model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)

import cv2
import torch
import numpy as np

import matplotlib.pyplot as plt
# %matplotlib inline

import warnings

def plot_preds(numpy_img, preds, color=(255, 0, 0)):


    boxes = preds['boxes'].detach().numpy()
    #numpy_img

    import warnings
    warnings.filterwarnings("ignore")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        for box in boxes:

            numpy_img = cv2.rectangle(
                np.array(numpy_img),
                (int(box[0]),int(box[1])),
                (int(box[2]),int(box[3])),
                (color[2], color[1], color[0]),
                2
            )

    return numpy_img


def detect_boxes(model, img_path, CONF_THRESH=0.8):

    model = model.eval()
    img_numpy = cv2.imread(img_path)[:,:,::-1]
    img = torch.from_numpy(img_numpy.astype('float32')).permute(2,0,1)
    img = img / 255.
    #print(img.shape)

    predictions = model(img[None,...])
    return predictions[0]['boxes'][predictions[0]['scores'] > CONF_THRESH]


def detect_img(model, img_path, CONF_THRESH=0.8, color=(255, 0, 255)):
    print('adad')
    model = model.eval()
    img_numpy = cv2.imread(img_path) # [:,:,::-1]
    img = torch.from_numpy(img_numpy.copy().astype('float32')).permute(2,0,1)
    img = img / 255.
    #print(img.shape)

    predictions = model(img[None,...])
    boxes = predictions[0]['boxes'][predictions[0]['scores'] > CONF_THRESH]

    boxes_dict = {}
    boxes_dict['boxes'] = boxes

    print('adad')
    img_with_boxes = plot_preds(img_numpy, boxes_dict, color) # np.array(open(img_path, 'rb').read())
    print('adad_pop')
    return img_with_boxes # .astype('uint')



@app.route('/<path:path>')
def send_js(path):
    print( path)
    return send_from_directory('./static', path)


@app.route('/detect-boxes',methods=['POST'])
def detect_1():
    fn = upload_file()
    r = detect_boxes(model, fn)
    return Response(json.dumps(r), mimetype="text/json")


def hexToRGB(str):
    h = str.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

@app.route('/detect-img',methods=['POST'])
def detect_2():
    fn = upload_file()

    print(request.values)

    if not(type(fn) == str):
        return fn

    print(hexToRGB('#ff0000'))

    r = detect_img(model, fn, int(request.values.get('threshold')) / 100.0, hexToRGB(request.values.get('color')))
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'response.jpg'), r)

    import base64

    #retval, buffer = cv2.imencode('.jpg', r)
    #jpg_as_text = base64.b64encode(buffer)
    #print(jpg_as_text)

    response = make_response(base64.b64encode(open('./tmp/response.jpg', 'rb').read()))
    #response.headers.set('Content-Type', 'text/json')
    return response

    response = make_response(open('./tmp/response.jpg', 'rb').read())
    response.headers.set('Content-Type', 'image/jpeg')
    response.headers.set('Content-Disposition', 'attachment', filename='%s.jpg' % 'response')
    return response


if __name__ == '__main__':
    app.run()
