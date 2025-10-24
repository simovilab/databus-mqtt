# databus-mqtt

MQTT broker for real-time transit vehicles tracking and telemetry data

## Overview

This repository provides a complete infrastructure for collecting real-time transit vehicle tracking and telemetry data using MQTT protocol. The system uses RabbitMQ as the MQTT broker and Redis as an in-memory database for quick data retrieval.

## Architecture

The system consists of three main components:

1. **RabbitMQ MQTT Broker**: Receives MQTT messages from transit vehicles
2. **Redis**: In-memory database for fast data storage and retrieval
3. **Subscriber Service**: Python service that subscribes to MQTT topics and stores data in Redis

```
Transit Vehicles → MQTT → RabbitMQ → Subscriber Service → Redis
                         (Port 1883)                    (Port 6379)
```

## Features

- **MQTT Protocol Support**: Full MQTT broker capabilities via RabbitMQ
- **Real-time Data Processing**: Immediate storage of vehicle tracking data
- **Fast Data Retrieval**: Redis in-memory storage for sub-millisecond access
- **Scalable Architecture**: Docker-based containerized services
- **Management Interface**: RabbitMQ management UI on port 15672
- **Automatic Reconnection**: Built-in retry logic for service reliability
- **TTL Support**: Automatic data expiration (1 hour default)

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/simovilab/databus-mqtt.git
cd databus-mqtt
```

2. Copy the environment file and adjust settings if needed:
```bash
cp .env.example .env
```

3. Start the services:
```bash
docker-compose up -d
```

4. Check service status:
```bash
docker-compose ps
```

## Configuration

### Environment Variables

Edit the `.env` file to customize the configuration:

- `RABBITMQ_USER`: RabbitMQ username (default: admin)
- `RABBITMQ_PASS`: RabbitMQ password (default: admin)
- `MQTT_TOPIC`: MQTT topic pattern to subscribe to (default: transit/vehicles/#)
- `REDIS_DB`: Redis database number (default: 0)

### RabbitMQ Configuration

RabbitMQ configuration is located in `config/rabbitmq/`:
- `enabled_plugins`: Enables MQTT and management plugins
- `rabbitmq.conf`: Main RabbitMQ configuration file

## Usage

### Accessing Services

- **RabbitMQ Management UI**: http://localhost:15672 (login with credentials from .env)
- **MQTT Port**: localhost:1883
- **Redis Port**: localhost:6379

### Publishing Test Messages

You can publish test messages using any MQTT client. Example using mosquitto_pub:

```bash
mosquitto_pub -h localhost -p 1883 -u admin -P admin \
  -t "transit/vehicles/bus/1234" \
  -m '{"vehicle_id": "1234", "lat": 40.7128, "lon": -74.0060, "speed": 25, "heading": 180}'
```

### Querying Data from Redis

Connect to Redis and query stored data:

```bash
docker exec -it databus-redis redis-cli

# Get all vehicle keys
KEYS vehicle:*

# Get data for a specific vehicle
GET vehicle:1234

# Get recent vehicles by timeline
ZRANGE vehicles:timeline -10 -1
```

## Data Storage Schema

The subscriber service stores data in Redis with the following structure:

- **Key Pattern**: `vehicle:{vehicle_id}`
- **Value**: JSON string containing vehicle data with metadata
- **TTL**: 1 hour (3600 seconds)
- **Timeline Index**: Sorted set `vehicles:timeline` for time-based queries

Example stored data:
```json
{
  "vehicle_id": "1234",
  "lat": 40.7128,
  "lon": -74.0060,
  "speed": 25,
  "heading": 180,
  "_timestamp": "2024-01-15T10:30:00.123456",
  "_topic": "transit/vehicles/bus/1234"
}
```

## Monitoring

### View Subscriber Logs

```bash
docker-compose logs -f subscriber
```

### View RabbitMQ Logs

```bash
docker-compose logs -f rabbitmq
```

### Check Redis Memory Usage

```bash
docker exec -it databus-redis redis-cli INFO memory
```

## Development

### Project Structure

```
databus-mqtt/
├── config/
│   └── rabbitmq/          # RabbitMQ configuration
│       ├── enabled_plugins
│       └── rabbitmq.conf
├── subscriber/            # MQTT subscriber service
│   ├── Dockerfile
│   ├── requirements.txt
│   └── subscriber.py
├── docker-compose.yml     # Docker Compose configuration
├── .env.example          # Environment variables template
└── README.md             # This file
```

### Extending the Subscriber

The subscriber service (`subscriber/subscriber.py`) can be extended to:
- Add custom data validation
- Implement additional storage backends
- Add data transformation logic
- Integrate with other services

## Stopping the Services

```bash
docker-compose down
```

To remove volumes as well:
```bash
docker-compose down -v
```

## Troubleshooting

### RabbitMQ won't start
- Check if ports 1883, 5672, or 15672 are already in use
- Verify Docker has sufficient resources

### Subscriber can't connect
- Ensure RabbitMQ is fully started (check `docker-compose logs rabbitmq`)
- Verify credentials in `.env` file
- Check network connectivity between containers

### Redis connection issues
- Verify Redis container is running: `docker-compose ps redis`
- Check Redis logs: `docker-compose logs redis`

## License

Apache License 2.0 - See LICENSE file for details
