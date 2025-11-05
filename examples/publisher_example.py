#!/usr/bin/env python3
"""
Example MQTT publisher for testing the databus-mqtt system.
This script publishes sample transit vehicle data to the MQTT broker.

Usage:
    pip install paho-mqtt
    python publisher_example.py
"""

import json
import time
import random
from datetime import datetime, UTC
import paho.mqtt.client as mqtt

# Configuration
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_USER = "admin"
MQTT_PASS = "admin"
MQTT_TOPIC_BASE = "transit/vehicles/bus"


def generate_vehicle_data(vehicle_id):
    """Generate sample vehicle tracking data"""
    # Simulate vehicle moving in NYC area
    lat = 40.7128 + random.uniform(-0.1, 0.1)
    lon = -74.0060 + random.uniform(-0.1, 0.1)

    return {
        "vehicle_id": vehicle_id,
        "route": f"Route-{random.randint(1, 10)}",
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "speed": round(random.uniform(0, 50), 1),
        "heading": random.randint(0, 359),
        "passengers": random.randint(0, 50),
        "timestamp": datetime.now(UTC).isoformat(),
    }


def on_connect(client, userdata, flags, rc, properties=None):
    """Callback for when the client connects to the broker"""
    if rc == 0:
        print(f"Connected to MQTT broker at {MQTT_HOST}:{MQTT_PORT}")
    else:
        print(f"Failed to connect, return code: {rc}")


def on_publish(client, userdata, mid, reason_code=None, properties=None):
    """Callback for when a message is published"""
    print(f"Message {mid} published successfully")


def main():
    """Main function to publish sample data"""
    print("Starting MQTT publisher example...")

    # Create MQTT client
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, client_id="example-publisher"
    )
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        # Connect to broker
        print(f"Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}...")
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()

        # Wait for connection
        time.sleep(2)

        # Publish messages for 5 different vehicles
        vehicle_ids = ["BUS-001", "BUS-002", "BUS-003", "BUS-004", "BUS-005"]

        print("\nPublishing vehicle data (press Ctrl+C to stop)...")
        message_count = 0

        while True:
            for vehicle_id in vehicle_ids:
                # Generate data
                data = generate_vehicle_data(vehicle_id)
                topic = f"{MQTT_TOPIC_BASE}/{vehicle_id}"

                # Publish message
                payload = json.dumps(data)
                result = client.publish(topic, payload, qos=1)

                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    message_count += 1
                    print(
                        f"[{message_count}] Published to {topic}: "
                        f"Vehicle {vehicle_id} at ({data['lat']}, {data['lon']}) "
                        f"Speed {data['speed']} km/h"
                    )
                else:
                    print(f"Failed to publish message to {topic}")

                # Wait a bit between messages
                time.sleep(1)

            # Wait before next round
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\nStopping publisher...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("Publisher stopped")


if __name__ == "__main__":
    main()
