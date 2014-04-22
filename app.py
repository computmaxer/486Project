import json

import xml.etree.ElementTree as ET

from flask import Flask
from flask import render_template

import requests
import logging


MARANTZ_IP = 'http://172.16.2.220'

app = Flask(__name__, static_url_path='/static/', static_folder='static')
app.template_folder = './'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data/')
def get_data():
    headers = {'referer': MARANTZ_IP + '/MainZone/index.html'}
    response = requests.get(MARANTZ_IP + '/goform/formMainZone_MainZoneXml.xml', headers=headers)

    volume = None
    input_source = None

    if response.status_code < 300 and response.status_code >= 200:
        logging.warning(response.content)
        root = ET.fromstring(response.content)
        for child in root:
            if child.tag == "MasterVolume":
                volume = float(child[0].text)
            elif child.tag == "InputFuncSelect":
                input_source = child[0].text
    return json.dumps({
        'volume': volume + 80,
        'input_source': input_source,
    })


if __name__ == '__main__':
    app.run(debug=True)
