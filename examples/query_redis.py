#!/usr/bin/env python3
"""
Example Redis query script for retrieving stored vehicle data.

Usage:
    pip install redis
    python query_redis.py
"""

import redis
import json
import sys

# Configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0


def connect_redis():
    """Connect to Redis"""
    try:
        client = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
        )
        client.ping()
        print(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        return client
    except redis.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
        sys.exit(1)


def print_vehicle_data(client, key):
    """Print vehicle data from a Redis key"""
    data = client.get(key)
    if data:
        vehicle_info = json.loads(data)
        print(f"\n{key}:")
        print(f"  Vehicle ID: {vehicle_info.get('vehicle_id', 'N/A')}")
        print(
            f"  Location: ({vehicle_info.get('lat', 'N/A')}, {vehicle_info.get('lon', 'N/A')})"
        )
        print(f"  Speed: {vehicle_info.get('speed', 'N/A')} km/h")
        print(f"  Heading: {vehicle_info.get('heading', 'N/A')}°")
        print(f"  Timestamp: {vehicle_info.get('_timestamp', 'N/A')}")
        print(f"  Topic: {vehicle_info.get('_topic', 'N/A')}")
    else:
        print(f"No data found for {key}")


def main():
    """Main function to query Redis data"""
    print("Redis Query Example\n" + "=" * 50)

    client = connect_redis()

    # Get all vehicle keys
    print("\nFetching all vehicle keys...")
    vehicle_keys = client.keys("vehicle:*")

    if not vehicle_keys:
        print("No vehicle data found in Redis.")
        print("Make sure the subscriber is running and receiving MQTT messages.")
        return

    print(f"Found {len(vehicle_keys)} vehicle(s) in Redis:")

    # Print each vehicle's data
    for key in sorted(vehicle_keys):
        print_vehicle_data(client, key)

    # Query timeline
    print("\n" + "=" * 50)
    print("Recent vehicles (from timeline):")
    timeline = client.zrange("vehicles:timeline", -10, -1, withscores=True)

    if timeline:
        for key, score in timeline:
            print(f"  {key} (last update: {score})")
    else:
        print("  No timeline data available")

    # Print statistics
    print("\n" + "=" * 50)
    print("Redis Statistics:")
    info = client.info("memory")
    print(f"  Memory used: {info['used_memory_human']}")
    print(f"  Total keys: {client.dbsize()}")


if __name__ == "__main__":
    main()
