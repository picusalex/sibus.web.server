#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket

from flask import Flask, make_response, jsonify, request

from sibus_lib import sibus_init, BusClient
from sibus_lib.utils import parse_num, datetime_now_float, handle_signals

SERVICE_NAME = "system.server"
logger, cfg_data = sibus_init(SERVICE_NAME)


class DicTopic:
    def __init__(self):
        self.reset()

    def reset(self):
        self.sibus_values = {}

    def safe_get_in_dict(self, key, ddict, safe=None):
        if key not in ddict:
            return safe
        return ddict[key]

    def get_cache_value(self, path_string, safe=None):
        logger.debug("Looking for cache value: %s" % path_string)
        path = path_string.strip("/").split("/")
        t = self.sibus_values
        for key in path[1:]:
            t = self.safe_get_in_dict(key, t)
            if t is None:
                logger.debug(" !!> Value not found for path: %s (near %s)" % (path_string, key))
                return safe
        logger.debug(" ==> Value found: %s" % unicode(t))
        return t

    def set_cache_value(self, path_string, value):
        logger.debug("Setting cache value: %s=%s" % (path_string, unicode(value)))
        path = path_string.strip("/").split("/")
        t = self.sibus_values
        for key in path[1:-1]:
            st = self.safe_get_in_dict(key, t)
            if st is None:
                t[key] = {}
                t = t[key]
            else:
                t = st
        t[path[-1]] = value
        pass


app = Flask(__name__)
sibus_values = DicTopic()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/torque', methods=['GET'])
def torque():
    pass
    return "OK!"


@app.route('/service/tts', methods=['GET'])
def action():
    logger.info("=========== Action request =============")
    for key in ["message"]:
        if key not in request.args:
            logger.error("!! GET /jeedom : Param '%s' not found" % key)
            return make_response(jsonify({'error': "Param '%s' not found" % key, 'status': 412}), 412)

    cmd_value = request.args["message"]

    cmd_topic = "sibus/action/multiroom/TTS"
    payload = {
        "value": cmd_value,
        "timestamp": datetime_now_float()
    }
    logger.info(" ++ TTS action request to MQTT: topic=%s, payload=%s" % (cmd_topic, str(payload)))
    if not busclient.mqtt_publish(topic=cmd_topic,
                                  payload=payload,
                                  retain=False):
        return make_response(jsonify({'error': "MQTT publish error", 'status': 500}), 500)

    return make_response(jsonify({
        'status': 0
    }), 200)

@app.route('/jeedom', methods=['GET'])
def jeedom():
    logger.info("=========== Jeedom call =============")
    for key in ["id", "name", "value"]:
        if key not in request.args:
            logger.error("!! GET /jeedom : Param '%s' not found" % key)
            return make_response(jsonify({'error': "Param '%s' not found" % key, 'status': 412}), 412)

    cmd_id = int(request.args["id"])
    cmd_name = request.args["name"]
    cmd_value = parse_num(request.args["value"])
    cmd_topic = "jeedom/%s" % cmd_name.strip("[").strip("]").replace("][", "/")
    old_value = sibus_values.get_cache_value(path_string=cmd_topic)
    cmd_timestamp = datetime_now_float()

    if cmd_value <> old_value or "force" in request.args:
        sibus_values.set_cache_value(path_string=cmd_topic, value=cmd_value)

        payload = {
            "value": cmd_value,
            "old": old_value,
            "timestamp": cmd_timestamp
        }
        logger.info(" ++ Jeedom to MQTT gateway: topic=%s, payload=%s" % (cmd_topic, str(payload)))
        if not busclient.mqtt_publish(topic="sibus/info/%s" % cmd_topic,
                                      payload=payload,
                                      retain=True):
            return make_response(jsonify({'error': "MQTT publish error", 'status': 500}), 500)
        update = True
    else:
        update = False

    return make_response(jsonify({
        'status': 0,
        'jeedom': {
            "id": cmd_id,
            "name": cmd_name,
            "value": cmd_value,
            "update": update
        }
    }), 200)


def on_busmessage(topic, payload):
    logger.info(payload)


if __name__ == '__main__':
    busclient = BusClient(socket.getfqdn(), SERVICE_NAME, onmessage_cb=on_busmessage)

    # busclient.mqtt_subscribe("sibus/jeedom/#")

    busclient.start()

    handle_signals()

    app.run(host="0.0.0.0", port=5000, debug=True)

    busclient.stop()
    logger.info("Terminated !")
