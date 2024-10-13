from flask import Flask, render_template, Response
from mqtt_client import MQTTClient
from database import Database
import json
import time
from datetime import datetime

app = Flask(__name__)
mqtt_client = MQTTClient()
db = Database()

def ensure_initial_data():
    data = db.get_latest_data()
    if not data:
        # Insert initial data if the database is empty
        db.insert_data(
            battery_level=100.0,
            is_live=False,
            total_runs=0,
            daily_runs=0
        )

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
            else:
                # If there's no data, send default values
                json_data = json.dumps({
                    'timestamp': datetime.now().isoformat(),
                    'battery_level': 0,
                    'is_live': False,
                    'total_runs': 0,
                    'daily_runs': 0
                })
                yield f"data: {json_data}\n\n"
            time.sleep(1)

    return Response(generate(), content_type='text/event-stream')

if __name__ == '__main__':
    ensure_initial_data()
    mqtt_client.start()
    app.run(debug=True, threaded=True)
