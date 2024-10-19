import paho.mqtt.client as paho
from paho import mqtt
import time
import os
import json
from threading import Thread

class MQTTHandler:
    def __init__(self):
        self.password = self.load_password()
        self.client = paho.Client()
        self.client.username_pw_set('coffeebot1', self.password)
        self.client.on_publish = self.on_publish
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.connect('www.advistatech.com', 10883)
        self.client.subscribe("coffeebot/robot-response", qos=0)
        self.client.loop_start()

    def load_password(self):
        try:
            password = os.environ['COFFEEBOT_MQTT_PASSWD']
            if password:
                return password
            else:
                print("Warning: COFFEEBOT_MQTT_PASSWD environment variable is set but empty.")
                return None
        except KeyError:
            print("Warning: COFFEEBOT_MQTT_PASSWD environment variable is not set.")
            return None

    def on_publish(self, client, userdata, mid):
        #print("publish: mid: "+str(mid))
        pass

    def on_connect(self, client, userdata, flags, rc, properties=None):
        print("connect: CONNACK received with code %s." % rc)

    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_message(self, client, userdata, msg):
        print("Message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    def publish_status(self, status_type, data):
        payload = json.dumps({
            "type": status_type,
            "data": data,
            "timestamp": time.time()
        })
        (rc, mid) = self.client.publish('coffeebot/status', payload=payload, qos=0)
        return rc, mid

    def report_position(self, x, y, theta):
        return self.publish_status("position", {"x": x, "y": y, "theta": theta})

    def report_speed(self, speed):
        return self.publish_status("speed", {"speed": speed})

    def report_battery(self, level):
        return self.publish_status("battery", {"level": level})

    def report_new_run(self, direction):
        return self.publish_status("new_run", {"direction": direction})

    def report_estop(self, activated):
        return self.publish_status("estop", {"activated": activated})

mqtt_handler = MQTTHandler()

def start_mqtt_loop():
    while True:
        time.sleep(1)

mqtt_thread = Thread(target=start_mqtt_loop)
mqtt_thread.daemon = True
mqtt_thread.start()
