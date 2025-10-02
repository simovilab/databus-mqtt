import os
import json
import time
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
import redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
MQTT_HOST = os.getenv('MQTT_HOST', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USER = os.getenv('MQTT_USER', 'admin')
MQTT_PASS = os.getenv('MQTT_PASS', 'admin')
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'transit/vehicles/#')

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Redis connection
redis_client = None

def connect_redis():
    """Connect to Redis with retry logic"""
    global redis_client
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True
            )
            redis_client.ping()
            logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
            return True
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    logger.error("Failed to connect to Redis after maximum retries")
    return False

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker"""
    if rc == 0:
        logger.info(f"Connected to MQTT broker at {MQTT_HOST}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        logger.info(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        logger.error(f"Failed to connect to MQTT broker, return code: {rc}")

def on_message(client, userdata, msg):
    """Callback for when a message is received from the broker"""
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        logger.info(f"Received message on topic '{topic}': {payload[:100]}...")
        
        # Parse JSON payload if applicable
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = {"raw": payload}
        
        # Add metadata
        data['_timestamp'] = datetime.utcnow().isoformat()
        data['_topic'] = topic
        
        # Store in Redis with topic-based key
        # Extract vehicle ID or use timestamp for unique key
        vehicle_id = data.get('vehicle_id', data.get('id', f"unknown_{int(time.time() * 1000)}"))
        redis_key = f"vehicle:{vehicle_id}"
        
        # Store the latest data for this vehicle
        redis_client.setex(
            redis_key,
            3600,  # TTL: 1 hour
            json.dumps(data)
        )
        
        # Also add to a sorted set for time-based queries
        redis_client.zadd(
            "vehicles:timeline",
            {redis_key: time.time()}
        )
        
        logger.info(f"Stored vehicle data in Redis: {redis_key}")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)

def on_disconnect(client, userdata, rc):
    """Callback for when the client disconnects from the broker"""
    if rc != 0:
        logger.warning(f"Unexpected disconnection from MQTT broker, return code: {rc}")
    else:
        logger.info("Disconnected from MQTT broker")

def main():
    """Main function to start the subscriber"""
    logger.info("Starting MQTT subscriber service...")
    
    # Connect to Redis
    if not connect_redis():
        logger.error("Cannot start without Redis connection")
        return
    
    # Create MQTT client
    client = mqtt.Client(client_id="databus-subscriber")
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Connect to MQTT broker with retry logic
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to MQTT broker (attempt {attempt + 1}/{max_retries})...")
            client.connect(MQTT_HOST, MQTT_PORT, 60)
            break
        except Exception as e:
            logger.warning(f"MQTT connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("Failed to connect to MQTT broker after maximum retries")
                return
    
    # Start the loop
    try:
        logger.info("Starting MQTT client loop...")
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        client.disconnect()
        logger.info("Subscriber service stopped")

if __name__ == "__main__":
    main()
