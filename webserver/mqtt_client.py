import paho.mqtt.client as mqtt
from database import Database

class MQTTClient:
    def __init__(self, broker_address="www.advistatech.com", broker_port=10883):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.db = Database()
        self.battery_level = 0
        self.is_live = False
        self.total_runs = 0
        self.daily_runs = 0

    def connect(self):
        self.client.connect(self.broker_address, self.broker_port, 60)

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        self.client.subscribe("coffeebot/battery")
        self.client.subscribe("coffeebot/status")
        self.client.subscribe("coffeebot/runs")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()

        if topic == "coffeebot/battery":
            self.battery_level = float(payload)
        elif topic == "coffeebot/status":
            self.is_live = payload.lower() == "true"
        elif topic == "coffeebot/runs":
            runs = payload.split(',')
            self.total_runs = int(runs[0])
            self.daily_runs = int(runs[1])

        self.db.insert_data(self.battery_level, self.is_live, self.total_runs, self.daily_runs)

    def start(self):
        self.connect()
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.db.close()

if __name__ == "__main__":
    mqtt_client = MQTTClient()
    mqtt_client.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopping MQTT client...")
        mqtt_client.stop()
