import json

import xml.etree.ElementTree as ET

from flask import Flask
from flask import render_template
from flask import request

import requests
import logging


MARANTZ_IP = 'http://172.16.2.220'
ROKU_IP = "http://172.16.2.210:8060"

app = Flask(__name__, static_url_path='/static/', static_folder='static')
app.template_folder = './'


@app.route('/')
def index():
    context = {
        'roku_ip': ROKU_IP
    }
    return render_template('index.html', **context)


@app.route('/data/')
def get_data():
    headers = {'referer': MARANTZ_IP + '/MainZone/index.html'}
    response = requests.get(MARANTZ_IP + '/goform/formMainZone_MainZoneXml.xml', headers=headers)

    volume = None
    input_source = None
    power_status = None
    sound_mode = None

    if response.status_code < 300 and response.status_code >= 200:
        logging.warning(response.content)
        root = ET.fromstring(response.content)
        for child in root:
            if child.tag == "MasterVolume":
                volume = float(child[0].text)
            elif child.tag == "InputFuncSelect":
                input_source = child[0].text
            elif child.tag == "Power":
                power_status = child[0].text
            elif child.tag == "selectSurround":
                sound_mode = child[0].text
    return json.dumps({
        'volume': volume + 80,
        'input_source': input_source,
        'power_status': power_status,
        'sound_mode': sound_mode.strip().replace(" ", "_"),
    })


@app.route('/set_source/', methods=['POST'])
def set_source():
    headers = {'referer': MARANTZ_IP + '/MainZone/index.html'}
    source = request.json.get('source')
    data = {
        'cmd0': "PutZone_InputFunction/%s" % source
    }
    response = requests.post(MARANTZ_IP + '/MainZone/index.put.asp', data=data, headers=headers)
    return json.dumps({'status': response.status_code})


@app.route('/send/', methods=['POST'])
def send_cmd():
    headers = {'referer': MARANTZ_IP + '/MainZone/index.html'}
    cmd = request.json.get('cmd')
    if cmd == "PutSurroundMode/MCHSTEREO":
        response = requests.get(MARANTZ_IP + '/goform/formiPhoneAppDirect.xml?MSMCH%20STEREO')
    else:
        data = {
            'cmd0': cmd
        }

        response = requests.post(MARANTZ_IP + '/MainZone/index.put.asp', data=data, headers=headers)
    return json.dumps({'status': response.status_code})


if __name__ == '__main__':
    app.run(debug=True)
