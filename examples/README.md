# Examples

This directory contains example scripts for testing and interacting with the databus-mqtt system.

## Files

### publisher_example.py

A sample MQTT publisher that generates and publishes simulated transit vehicle data.

**Usage:**
```bash
pip install paho-mqtt
python publisher_example.py
```

This script will:
- Connect to the MQTT broker
- Publish simulated vehicle tracking data for 5 buses
- Continue publishing until stopped with Ctrl+C

### query_redis.py

A sample script to query and display vehicle data stored in Redis.

**Usage:**
```bash
pip install redis
python query_redis.py
```

This script will:
- Connect to Redis
- Display all stored vehicle data
- Show timeline information
- Print Redis statistics

## Testing the System

1. Start the databus-mqtt system:
```bash
docker-compose up -d
```

2. Run the publisher example in one terminal:
```bash
python examples/publisher_example.py
```

3. Run the query script in another terminal to see the stored data:
```bash
python examples/query_redis.py
```

4. You can also check the subscriber logs:
```bash
docker-compose logs -f subscriber
```
