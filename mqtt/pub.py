#!/usr/bin/python3 
import paho.mqtt.client as paho
from paho import mqtt
import time,os

password=""

def load_password():
    global password
    """
    Load the MQTT password from the COFFEEBOT_MQTT_PASSWD environment variable.
    Returns:
        str: The password value, or None if the environment variable is not set.
    """
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


def on_publish(client, userdata, mid):
    print("publish: mid: "+str(mid))

def on_connect(client, userdata, flags, rc, properties=None):
    print("connect: CONNACK received with code %s." % rc)

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    print("Message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

load_password()
client = paho.Client()
client.username_pw_set('coffeebot1', password)
client.on_publish = on_publish
client.on_connect= on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect('www.advistatech.com', 10883)
client.subscribe("coffeebot/robot-response", qos=0)

(rc, mid) = client.publish('coffeebot/robot-request', payload="hot1", qos=0)
client.loop_start()
while True:
    print("looping")
    time.sleep(1)
