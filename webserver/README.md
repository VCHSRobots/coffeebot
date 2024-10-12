# CoffeeBot Webserver

This webserver displays statistics for the CoffeeBot, including battery level, live status, total coffee runs, and daily coffee runs. It uses MQTT to receive updates and stores the data in a SQLite database.

## Setup

1. Make sure you have Python 3.7+ installed on your system.

2. Navigate to the `webserver` directory:
   ```
   cd webserver
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Webserver

1. Start the Flask application:
   ```
   python app.py
   ```

2. The webserver should now be running. You can access it by opening a web browser and navigating to:
   ```
   http://localhost:5000
   ```

3. The dashboard will display the latest CoffeeBot statistics and update in real-time as new data is received via MQTT.

## Notes

- Make sure your MQTT broker is running and accessible at `localhost:1883`. If your MQTT broker is running on a different address or port, update the `broker_address` and `broker_port` in `mqtt_client.py`.

- The webserver expects MQTT messages on the following topics:
  - `coffeebot/battery`: Battery level (float)
  - `coffeebot/status`: Live status (boolean)
  - `coffeebot/runs`: Total runs and daily runs (comma-separated integers)

- The SQLite database file `coffeebot.db` will be created in the same directory as `app.py` when the application runs for the first time.
