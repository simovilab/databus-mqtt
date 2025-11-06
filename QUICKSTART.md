# Quick Start Guide

This guide will help you get the databus-mqtt system up and running in minutes.

## Prerequisites

- Docker (20.10 or later)
- Docker Compose (or Docker with Compose plugin)

## Installation Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/simovilab/databus-mqtt.git
   cd databus-mqtt
   ```

2. **Configure environment (optional)**

   ```bash
   cp .env.example .env
   # Edit .env if you want to change default settings
   ```

3. **Start all services**

   ```bash
   docker-compose up -d
   ```

4. **Verify services are running**

   ```bash
   docker-compose ps
   ```

   You should see three containers running:

   - `databus-mqtt-rabbitmq` - MQTT broker
   - `databus-mqtt-redis` - In-memory database
   - `databus-mqtt-subscriber` - MQTT to Redis bridge

## Testing the System

### 1. Access RabbitMQ Management UI

Open your browser and navigate to: http://localhost:15672

- Username: `admin` (or value from .env)
- Password: `admin` (or value from .env)

### 2. Publish Test Messages

Install the paho-mqtt library:

```bash
pip install paho-mqtt
```

Run the example publisher:

```bash
python examples/publisher_example.py
```

This will start publishing simulated vehicle tracking data.

### 3. Query Stored Data

Install the redis library:

```bash
pip install redis
```

Run the query example:

```bash
python examples/query_redis.py
```

This will display all vehicle data stored in Redis.

### 4. Monitor Subscriber Logs

Watch the subscriber service process messages:

```bash
docker-compose logs -f subscriber
```

## Common Commands

### View all logs

```bash
docker-compose logs -f
```

### Stop all services

```bash
docker-compose down
```

### Restart a service

```bash
docker-compose restart subscriber
```

### View Redis data directly

```bash
docker exec -it databus-redis redis-cli
# Then run Redis commands like:
# KEYS *
# GET vehicle:BUS-001
```

## Next Steps

- Customize the MQTT topic in `.env` file
- Modify `subscriber/subscriber.py` to add custom processing logic
- Integrate with your transit vehicle tracking system
- Add additional services to the Docker Compose file

## Troubleshooting

**Services won't start:**

- Check if ports 1883, 5672, 6379, or 15672 are already in use
- Ensure Docker has sufficient resources allocated

**Can't connect to MQTT broker:**

- Wait 30 seconds for RabbitMQ to fully initialize
- Check logs: `docker-compose logs rabbitmq`

**No data in Redis:**

- Ensure the subscriber is running: `docker-compose ps subscriber`
- Check subscriber logs: `docker-compose logs subscriber`
- Verify you're publishing to the correct topic

## Support

For issues and questions, please open an issue on GitHub.
