#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import signal
import sys

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

from sibus_lib import sibus_init, SmartConfigFile, MessageObject, BusElement
from sibus_lib.utils import float_to_datetime

sys.path.append(os.getenv('ALPIBUS_DIR', os.getcwd()))

SERVICE_NAME = "web.server"
logger, cfg_data = sibus_init(SERVICE_NAME)

cfg_server = SmartConfigFile(SERVICE_NAME+".yml")

TEMPLATE_FOLDER = cfg_server.get(["flask_paths", "templates"], os.path.join(os.getcwd(),"flask/templates"))
STATIC_FOLDER = cfg_server.get(["flask_paths", "static"], os.path.join(os.getcwd(),"flask/static"))

WEB_SERVER_PORT = cfg_server.get(["web_server", "port"], 5000)
WEB_SECRET_KEY = cfg_server.get(["web_server", "secret_key"], "lkzjeflkjzlkjvalkenclukanevluknzrevlknzlkncklzenc")

logger.info("Configure Web server    templates, %s"%(TEMPLATE_FOLDER))
logger.info("Configure Web server static files, %s"%(STATIC_FOLDER))

app = Flask(SERVICE_NAME.replace(".", "_"),
            template_folder=TEMPLATE_FOLDER,
            static_folder=STATIC_FOLDER)
app.config['SECRET_KEY'] = WEB_SECRET_KEY
socketio = SocketIO(app)
app.config['SIBUS_DEBUG'] = False

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/')
@app.route('/index.html')
def index():
    """Serve the client-side application."""
    return render_template('default.html')

@app.route('/domotic.dashboard.html')
def domotic_dashboard():
    """Serve the client-side application."""
    return render_template('domotic.dashboard.html')

@app.route('/bus_live_comm.html')
def bus_live_comm():
    """Serve the client-side application."""
    app.config['SIBUS_DEBUG'] = True
    return render_template('bus_live_comm.html')

@app.route('/bus_test_comm.html')
def bus_test_comm():
    """Serve the client-side application."""
    return render_template('bus_test_comm.html')

@app.route('/system.monitor.html')
def system_monitor():
    """Serve the client-side application."""
    return render_template('system.monitor.html')

@app.route('/bus_command',methods=['POST'])
def bus_command():
    if request.method == 'POST':
        # use Flask's build in json decoder
        the_dict = request.get_json()
        if "topic" not in the_dict:
            raise InvalidUsage("Missing mandatory field 'topic'", status_code=410)

        msg_data = {}
        for k in the_dict:
            if k == "topic":
                continue
            msg_data[k] = the_dict[k]

        message = MessageObject(data=msg_data, topic=the_dict["topic"])
        busclient.publish(message)

    return jsonify({'status': "OK"})


@app.route('/speak/<message>')
def speak_command(message):
    message = MessageObject(data={"tts": message}, topic="request.audio.tts")
    busclient.publish(message)

    return jsonify({'status': "OK"})

@socketio.on('connect')
def connect():
    print("connect ")

__DEBUG = False
@socketio.on('message')
def message(json):
    if "topic" not in json or "data" not in json:
        return

    message = MessageObject(data=json["data"], topic=json["topic"])
    busclient.publish(message)

@socketio.on('disconnect')
def disconnect():
    app.config['SIBUS_DEBUG'] = False
    print('disconnect')

def on_busmessage(message):
    try:
        t = float_to_datetime(message.date_creation)

        if app.config['SIBUS_DEBUG']:
            tmp_data = message.get_data()
            if tmp_data is not None and len(tmp_data) > 256:
                data = "long data: %d" % len(tmp_data)
            else:
                data = tmp_data

            socketio.emit("sibus_debug", {
                "host": message.origin_host,
                "service": message.origin_service,
                "date": t.isoformat(),
                "topic": message.topic,
                "data": data
            })

        if message.topic.startswith("error"):
            socketio.emit("error", {
                "host": message.origin_host,
                "service": message.origin_service,
                "date": t.isoformat(),
                "topic": message.topic,
                "data": message.get_data()
            })

        socketio.emit(message.topic, {
            "host": message.origin_host,
            "service": message.origin_service,
            "date": t.isoformat(),
            "topic": message.topic,
            "data": message.get_data()
        })

        pass
    except:
        pass
    pass

def sigterm_handler(_signo=None, _stack_frame=None):
    busclient.stop()
    logger.info("Program terminated correctly")
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)


if __name__ == '__main__':
    busclient = BusElement(SERVICE_NAME, callback=on_busmessage, ignore_my_msg=False)
    busclient.register_topic("*")
    
    busclient.start()

    socketio.run(app, host="0.0.0.0", port=WEB_SERVER_PORT)

sigterm_handler()

