import asyncio
import socketio
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Socket.IO client for testing
sio = socketio.AsyncClient()

@sio.event
async def connect():
    logger.info("Connected to server")

@sio.event
async def disconnect():
    logger.info("Disconnected from server")

@sio.event
async def data(data):
    logger.info(f"Received data: {data}")

async def main():
    try:
        # Connect to the server
        await sio.connect('http://localhost:8000')
        logger.info("Starting test...")
        
        # Send start event
        await sio.emit('simulation:start')
        logger.info("Sent simulation:start event")
        
        # Wait for data for 10 seconds
        await asyncio.sleep(10)
        
        # Disconnect
        await sio.disconnect()
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        await sio.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 