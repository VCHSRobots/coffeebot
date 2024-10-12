from flask import Flask, render_template, Response
from mqtt_client import MQTTClient
from database import Database
import json
import time

app = Flask(__name__)
mqtt_client = MQTTClient()
db = Database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats')
def stats():
    def generate():
        while True:
            data = db.get_latest_data()
            if data:
                _, timestamp, battery_level, is_live, total_runs, daily_runs = data
                json_data = json.dumps({
                    'timestamp': timestamp,
                    'battery_level': battery_level,
                    'is_live': is_live,
                    'total_runs': total_runs,
                    'daily_runs': daily_runs
                })
                yield f"data: {json_data}\n\n"
            time.sleep(1)

    return Response(generate(), content_type='text/event-stream')

if __name__ == '__main__':
    mqtt_client.start()
    app.run(debug=True, threaded=True)
